from django.db.models.query_utils import Q
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Item, Category, Department, ItemAssignment, Profile, ItemHistory
from .forms import AddItemForm, AddAccessoryForm, CustomUserCreationForm, PasswordResetForm, SetPasswordForm, ProfileForm, CategoryForm
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import date
from .tokens import account_activation_token
import re
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from datetime import date
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, ExtractYear
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from .tasks import send_email_task


# Function to check if the user is head of some department
def is_department_head(user):
    """
    Function to check if the user 
    is the head of the department or not 
    """
    department = Department.objects.filter(head=user).first()
    return department is not None


# Dashboard View
@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def homeView(request):
    """
    This view is for dashboard page,
    It contains, statistics, 
    graphs and tables about 
    the items and categories
    """

    # find the department by user
    department = Department.objects.filter(head=request.user).first()
    if department is None:
        return redirect('profile')

    # filter items by department
    items = Item.objects.filter(department=department)

    # Data for the Items Added Graph (Line Chart)
    items_with_year = items.annotate(year=ExtractYear(
        'date_received')).values('year').distinct()
    years = [item['year'] for item in items_with_year]

    # Prepare the data for the Category chart (BAR)
    categories = Category.objects.filter(department=department).annotate(
        total_quantity=Sum('item__quantity'))
    category_names = [category.name for category in categories]
    item_quantities = [
        category.total_quantity if category.total_quantity else 0 for category in categories]

    # Prepare data for Item Types chart (PIE)
    item_types_data = (items.values('item_type').annotate(
        item_count=Sum('quantity')).order_by('item_type'))
    type_label = [types['item_type'] for types in item_types_data]
    type_data = [types['item_count'] if types['item_count']
                 else 0 for types in item_types_data]

    # Broken Items Count
    broken_items = items.filter(status='broken')
    recently_checked_out_items = ItemAssignment.objects.filter(
        department=department, action="assign", status="out")

    context = {
        "title": "Dashboard",
        "available_count": items.filter(status='available').count(),
        "checked_out_count": items.filter(status='outinuse').count(),
        "broken_count": broken_items.count(),
        "total_count": items.all().count(),
        "recently_checked_out_items": recently_checked_out_items.order_by('-date')[:10],
        "broken_items": broken_items[:10],
        "items_in_shortage": items.filter(Q(item_type="accessory") | Q(item_type="consumable")).order_by("quantity")[:10],
        "items_due_return": recently_checked_out_items.order_by("due_date")[:10],
        "category_names": category_names,
        'item_quantities': item_quantities,
        'type_label': type_label,
        'type_data': type_data,
        'years': years,
    }
    return render(request, "dashboard.html", context)


def get_monthly_added_items_data(request, year):
    """
    This view is for Item Added Graph,
    this will recieve the ajax request and
    responcse as json with data, 
    to make the filtering faster.

    """

    # find the department by user
    department = Department.objects.filter(head=request.user).first()

    # if the user is not the head of department dont show anything
    if department is None:
        months = []
        items_added = []
    else:
        # filter items for the department
        items = Item.objects.filter(department=department)
        monthly_data = (
            items.filter(date_received__year=year)
            .annotate(month=TruncMonth('date_received'))
            .values('month')
            .annotate(items_added=Count('id'))
            .order_by('month')
        )

        # Data for the graph (labels and data)
        months = [data['month'].strftime('%B') for data in monthly_data]
        items_added = [data['items_added'] for data in monthly_data]

    data = {
        'months': months,
        'items_added': items_added,
    }

    return JsonResponse(data)


# ------------------------------ ITEMS ------------------------------------------------

# Single Items
@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def items(request):
    """
    items view is for Items page,
    where it shows, tables with items,
    fillters and search bars

    """

    # get the department
    department = Department.objects.filter(head=request.user).first()
    items = Item.objects.filter(department=department)

    # get the filter information
    category = request.GET.get("category")
    status = request.GET.get("status")
    item_type = request.GET.get("item_type")
    date_received = request.GET.get("date_recieved")

    # input from the search field
    q = request.GET.get("q")

    # make dictionary out of search and filter inputs, to pass them back to page
    # for saving the filters status
    search_filters = {
        "category": category if category is not None else "",
        "status": status if status is not None else "",
        "item_type": item_type if item_type is not None else "",
        "date_recieved": date_received if date_received is not None else "",
        "q": q if q is not None else "",
    }

    # Filter items according to users inputs (filter and search)
    items_list = items.filter(
        Q(category__name__contains=search_filters["category"]) &
        Q(status__contains=search_filters["status"]) &
        Q(item_type__contains=search_filters["item_type"]) &
        Q(date_received__contains=search_filters["date_recieved"])
    ).filter(
        Q(item_name__contains=search_filters["q"]) |
        Q(location__contains=search_filters["q"]) |
        Q(description__contains=search_filters["q"]) |
        Q(notes__contains=search_filters["q"]) |
        Q(vendor__contains=search_filters["q"])
    )

    # paginator (for items table)
    page = request.GET.get('page', 1)
    # Default to 50 items per page
    items_per_page = request.GET.get('items_per_page', 50)
    # Show 50 items per page
    paginator = Paginator(items_list, items_per_page)

    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        data = paginator.page(1)
    except EmptyPage:
        # If the page parameter is out of range, show the last page of results
        data = paginator.page(paginator.num_pages)

    # pass the data to the page
    context = {
        "title": "Items",
        "items": data,
        'items_per_page': items_per_page,
        "total_count": items.count(),
        "broken_count": items.filter(status="broken").count(),
        "available_count": items.filter(status="available").count(),
        "inuse_count": items.filter(status="outinuse").count(),
        "categories": Category.objects.all().filter(department=department),
        "search_filters": search_filters
    }
    return render(request, 'items/items.html', context)


# function for adding new Items to DB
@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def add_item(request):
    """
    View to add new Items (Single items),
    to the db
    """

    # get the department
    department = Department.objects.get(head=request.user)

    # process the form
    if request.method == "POST":
        form = AddItemForm(request.POST, request.FILES)

        # Do the validation
        if form.is_valid():
            item = form.save(commit=False)

            # set category
            cat = Category.objects.filter(department=department).filter(
                name=request.POST.get("category"))
            item.category = cat[0]
            item.department = department

            # set type as asset (single item)
            item.item_type = "asset"
            item.save()
            messages.success(request, 'Item added successfully')
            return redirect('items')

        # if form is not valid show errors
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, error)

    # pass data
    context = {
        "title": "New Item",
        "categories": Category.objects.filter(department=department),
        "form": AddItemForm(),
    }
    return render(request, "items/add_new_item.html", context)


# function to add (bulk items)
@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def add_accessory(request):
    """
    View to add new Items (bulk items),
    to the db
    """

    department = Department.objects.get(head=request.user)
    if request.method == "POST":
        form = AddAccessoryForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            cat = Category.objects.filter(department=department).filter(
                name=request.POST.get("category"))
            item.category = cat[0]
            item.department = department
            item.item_type = "accessory"
            item.save()
            messages.success(request, 'Item added successfully')
            return redirect('items')

        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, error)
    context = {
        "title": "New Accessory",
        "add_url": "add_accessories",
        "categories": Category.objects.filter(department=department),
        "form": AddAccessoryForm(),
    }
    return render(request, "items/add_new_accessory.html", context)

# function to add (consumable)


@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def add_consumable(request):
    """
    View to add new Items (Consumables),
    to the db
    """
    department = Department.objects.get(head=request.user)
    if request.method == "POST":
        form = AddAccessoryForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            cat = Category.objects.filter(department=department).filter(
                name=request.POST.get("category"))
            item.category = cat[0]
            item.department = department
            item.item_type = "consumable"
            item.save()
            messages.success(request, 'Item added successfully')
            return redirect('items')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, error)
    context = {
        "title": "New Consumable",
        "categories": Category.objects.filter(department=department),
        "add_url": "add_consumables",
        "form": AddAccessoryForm(),
    }
    return render(request, "items/add_new_accessory.html", context)

# function to update assets


@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def update(request, pk):
    """
    View to update Assets (single items)
    """
    department = Department.objects.get(head=request.user)
    item = Item.objects.get(id=pk)

    if request.method == "POST":
        form = AddItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            cat = Category.objects.filter(department=department).filter(
                name=request.POST.get("category"))
            item.category = cat[0]
            item.save()
            messages.success(request, 'Item Edited !')
            return redirect('item_detail', pk)

        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, error)

    context = {
        "title": "Edit Item",
        "categories": Category.objects.filter(department=department),
        "form": AddItemForm(instance=item),
        "item": item,
    }
    return render(request, "items/update_item.html", context)

# function to add bulk items and consumables


@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def update_consumables(request, pk):
    """
    View to update consumables and accessories (items in  bulk)
    """
    department = Department.objects.get(head=request.user)
    item = Item.objects.get(id=pk)

    if request.method == "POST":
        form = AddAccessoryForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            cat = Category.objects.filter(department=department).filter(
                name=request.POST.get("category"))
            item.category = cat[0]
            item.save()
            messages.success(request, 'Item Edited !')
            return redirect('item_detail', pk)

        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, error)
    context = {
        "title": "Edit Item",
        "categories": Category.objects.filter(department=department),
        "form": AddAccessoryForm(instance=item),
        "item": item,
    }
    return render(request, "items/update_consumable.html", context)


# function for item details
@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def item_detail(request, pk):
    """
    View for detail page of the items
    Where admin can perform, crud operations on items
    plus check in and out

    """

    # Get the item
    item = Item.objects.get(id=pk)

    # get checked out items
    checked_out_items = ItemAssignment.objects.filter(
        item=item, action="assign", status='out')

    # get the history of the items
    item_history = ItemHistory.objects.filter(item=item)

    # pass information to the page
    context = {
        "title": f"{item.item_name} Detail",
        "item": item,
        "checked_out_items": checked_out_items,
        'item_history': item_history,

    }

    return render(request, "items/item_detail.html", context)


# Bulk Delete
@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def delete_items(request, pk=None):
    if request.method == "POST":
        checked_items = request.POST.getlist("item_id")
        print(checkin_items)
        if len(checked_items) > 0:
            Item.objects.filter(id__in=checked_items).delete()
        return redirect('items')
    else:
        Item.objects.filter(id=pk).delete()
        return redirect('items')


# Check Out
@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def checkout_items(request, pk):
    """
    This view is for checking out the items
    or assigning items to someone 
    """
    # Extract informatin fromt the form
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        item = Item.objects.get(id=item_id)
        quantity = request.POST.get("quantity")
        department = item.department
        location = request.POST.get("location")
        requestor_id = request.POST.get("requestor")
        requestor = User.objects.get(id=requestor_id)
        done_by = request.user
        due_date = request.POST.get("due_date") or None

        notes = request.POST.get("notes")
        item.location = location

        # update the item owner
        item.holder.add(requestor)

        # alter the status of the item
        if item.item_type == "asset":
            item.status = "outinuse"
        else:
            if int(item.quantity)-int(quantity) == 0:
                item.status = "outinuse"
            item.quantity = int(item.quantity)-int(quantity)
        # save the item
        item.save()

        # if the quantity of items is less then min_alert
        #  it will send email notifications
        if item.min_alert_quantity > 0:
            if item.quantity <= item.min_alert_quantity:
                subject = f"{item}:Items in Shortage"
                message = f"Dear Admin, the following item is in shortage:\n{item}\t{item.quantity} available"
                recipient_list = [item.department.head.email]
                send_email_task.delay(subject, message, recipient_list)

        # create new Transaction
        item_out = ItemAssignment(
            item=item,
            quantity=quantity,
            action="assign",
            department=department,
            location=location,
            requestor=requestor,
            done_by=done_by,
            due_date=due_date,
            notes=notes,
            status='out',
        )
        item_out.save()

        # Save to the item story
        ItemHistory.objects.create(item=item, transaction=item_out)

        # Send email to the user about the new transaction
        subject = f"{item}"
        message = f"Dear {requestor.first_name},\nNew Items was assigned to you:\n{item}----{quantity}---{location}---{due_date}\nNotes: {notes}\nBy: {done_by} at {date}"
        recipient_list = [requestor.email]
        send_email_task.delay(subject, message, recipient_list)

        messages.success(request, 'Checked Out Successfully')
        return redirect("item_detail", item.id)

    users = User.objects.filter(is_active=True)
    context = {
        "item": Item.objects.get(id=pk),
        "users": users,
        "today": date.today()
    }
    return render(request, "items/checkout.html", context)


# Check in View
@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def checkin_items(request, pk):
    """
    This view is for handling items check in
    or when the items are returned

    """
    assingment = ItemAssignment.objects.get(id=pk)
    # Extract the data
    if request.method == "POST":
        item = assingment.item
        notes = request.POST.get("notes")
        quantity = assingment.quantity
        location = "storage"
        requestor = assingment.requestor
        done_by = request.user
        due_date = None

        # Change Item in DB
        item.location = location
        item.holder.remove(requestor)
        if item.item_type == "asset":
            if item.status != 'broken':
                item.status = "available"
        else:
            if int(item.quantity)+int(quantity) > 0:
                item.status = "available"
            item.quantity = int(item.quantity)+int(quantity)
        item.save()

        # create new Transaction
        item_in = ItemAssignment(
            item=item,
            quantity=quantity,
            action="return",
            department=assingment.department,
            location=location,
            requestor=requestor,
            done_by=done_by,
            due_date=due_date,
            notes=notes,
        )
        item_in.save()

        # change the status of checked out item
        assingment.status = 'in'
        assingment.save()

        # Save to the item story
        ItemHistory.objects.create(item=item, transaction=item_in)

        # Redirect
        subject = f"{item}"
        message = f"Dear {requestor.first_name},\nItem was returned:\n{item}----{quantity}\nNotes: {notes}\nBy: {done_by}"
        recipient_list = [requestor.email]
        send_email_task.delay(subject, message, recipient_list)

        messages.success(request, 'Checked In Successfully')
        return redirect("item_detail", item.id)

    # users = User.objects.all()
    context = {
        "item": assingment,
        "today": date.today()
    }
    return render(request, "items/checkin.html", context)

# item broken view: To report the item is broken


@login_required(login_url='login/')
def item_outoforder(request, pk):
    item = Item.objects.get(id=pk)
    item.status = "broken"
    item.save()
    subject = f"{item} Out of Order"
    message = f"Report: {item} is out of order\nLocation: {item.location}."
    recipient_list = [item.department.head.email]
    send_email_task.delay(subject, message, recipient_list)

    messages.success(request, 'Report sent to Admin successfully!')
    return redirect("item_detail", item.id)


# item fixed view
@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def item_fixed(request, pk):
    item = Item.objects.get(id=pk)
    if item.location == 'storage':
        item.status = "available"
    else:
        item.status = "outinuse"
    item.save()
    messages.success(request, 'Report sent to Admin successfully!')
    return redirect("item_detail", item.id)


@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
# PDF of qr codes
def generate_pdf(request):
    """
    View to generate pdf of qr codes and 
    allow customization of the page
    """
    # handle the form
    if request.method == "POST":
        # page configurations
        checked_items = request.POST.getlist("item_id")
        size = request.POST.get("size")
        gap = request.POST.get("gap")
        mx = request.POST.get("mx")
        my = request.POST.get("my")

        # Create a file-like buffer to receive PDF data.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="qrcodes.pdf"'

        # Create the PDF object, using the response object as its "file."
        p = canvas.Canvas(response, pagesize=A4, bottomup=1)

        # p.setPageRotation(180)
        items = Item.objects.filter(id__in=checked_items)

        # image_paths =  [(settings.MEDIA_ROOT + 'qrcode/' + items) for i in range(100) ]
        # Define a list of image paths
        image_paths = list(
            map(lambda item: settings.MEDIA_ROOT + 'qrcode/' + item.qr_code, items))
        image_width = int(size)
        image_height = int(size)
        padding = int(gap)
        p.translate(0, A4[1]-image_height)
        x = 0+int(mx)
        y = 0-int(my)

        # putting the qr codes in the page according to configurations
        for i in range(len(image_paths)):
            image = ImageReader(image_paths[i])
            p.drawImage(image, x, y, width=image_width,
                        height=image_height, showBoundary=True)

            x += (image_width+padding)
            if (x+image_width+padding+int(mx)) > A4[0]:
                if (y-(2*image_height+padding+int(my))) <= -A4[1]:
                    p.showPage()
                    p.translate(0, A4[1]-image_height)
                    x = 0+int(mx)
                    y = 0-int(my)
                else:
                    y -= (image_height+padding)
                    x = 0+int(mx)

        p.showPage()
        # Close the PDF object cleanly, and we're done.
        p.save()

        return response

    # return it as pdf page
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="qrcodes.pdf"'
    return response


@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
# qr code printing page
def print_qr(request, pk=None):
    """
    View to show the print QR codes page
    """

    # get the selected items and show the page
    checked_items = request.POST.getlist("item_id")
    if pk is not None:
        checked_items.append(pk)
    context = {
        "items": Item.objects.filter(id__in=checked_items),
        "all_items": Item.objects.all().exclude(id__in=checked_items),
    }

    return render(request, "items/print_qrcodes.html", context)


# function to send an email to the user for confirmation
def activateEmail(request, user, to_email):
    """
    Function to send confirmation email to the user
    """
    mail_subject = 'Activate your user account.'
    message = render_to_string('auth/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    recipient_list = [to_email]
    send_email_task.delay(mail_subject, message, recipient_list)

    messages.success(
        request, f'Dear user, please check your inbox and click on activation link to confirm and complete the registration. Check your spam folder!')
    # else:
    #     messages.error(
    #         request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')


# Registration
def register(request):
    """
    View to handle the registration of new users
    """
    # handle registrantion form
    if request.method == 'POST':
        email = request.POST['email']
        # Validate email, it should be UCA email only!
        if not re.match(r'^[a-zA-Z]+\.[a-zA-Z]+(_\d{4})?@ucentralasia\.org$', email):
            messages.error(request, 'Please enter a valid UCA email address.')
            return redirect("register")

        # Extract data first name and last name from the email
        first_name, last_name = email.split('@')[0].split('.')
        if "_" in last_name:
            last_name = last_name.split("_")[0]

        # handle the form (create the user but it should not be active)
        # after email confirmation it becomes active
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.username = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # call the activateEmail function that will send email to the user
            # to confirm
            activateEmail(request, user, form.cleaned_data.get('email'))

            # need to change to be redirected the special page
            return redirect('login')

        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, error)

    form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form, "title": "Registration", })


# Confirms email and makes the user active
def activate(request, uidb64, token):
    """
    View to active the user account
    """
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Check the token
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        Profile.objects.create(owner=user)

        # Notify user about account activation
        
        subject= "Accaunt Created"
        message = f"Dear {user.first_name},\nYour accaunt is creataed successfully"
        recipient_list=[user.email]
        send_email_task.delay(subject, message, recipient_list)

        messages.success(
            request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')

    return redirect('home')


# login view
def auth(request):
    """
    Login view, handles the login form and
    redirects accordingly 
    """
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}!')
            department = Department.objects.filter(head=user).first()
            if department is not None:
                # Redirect to admin dashboard if user is the head of a department
                return redirect('home')
            else:
                # Redirect to profile page if user is not the head of a department
                return redirect('profile')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, "auth/login.html")

# view to change your password


def password_change(request):
    """
    View to change your password
    """

    # get the user
    user = request.user

    # handle the form and change the passowrd
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()

            # notify user about the password change
            messages.success(request, "Your password has been changed")
            subject = "Password Changed"
            message= f"Dear {user.first_name},\nYour password is changed successfully"
            to=[user.email]
            send_email_task(subject, message, to)
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'auth/recover_password.html', {'form': form})


# view to reset the passowrd
def password_reset_request(request):
    """
    This view will send request to reset your password
    by email confirmation
    """

    # handle the form
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # get the user email
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()

            # if there is a user with this email, send email to that user to confirm
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("auth/template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })

                recipient_list = [associated_user.email]
                send_email_task.delay(subject, message, recipient_list)
                messages.success(request,
                                 """
                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                            You should receive them shortly.If you don't receive an email, please make sure you've entered the address 
                            you registered with, and check your spam folder.
                        """
                                 )

                # if email.send():
                #     messages.success(request,
                #                      """
                #             We've emailed you instructions for setting your password, if an account exists with the email you entered.
                #             You should receive them shortly.If you don't receive an email, please make sure you've entered the address
                #             you registered with, and check your spam folder.
                #         """
                #                      )
                # else:
                #     messages.error(
                #         request, "Problem sending reset password email, <b>SERVER PROBLEM</b>")

            return redirect('home')

    form = PasswordResetForm()
    return render(request, "auth/forgot_password.html", context={"form": form})


# View to confirm the email and change the password
def passwordResetConfirm(request, uidb64, token):
    """
    View to confirm the email and change the password
    """

    # get the user
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    # handle the form and change the password
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()

                # notify the user about the successfull password change
                
                subject="Password  reset"
                message = f"Dear {user.first_name},\nYour password is reset successfully" 
                to=[user.email]
                send_email_task.delay(subject, message, to)
                messages.success(
                    request, "Your password has been set. You may go ahead and log in  now.")
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'auth/recover_password.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(
        request, 'Something went wrong')
    return redirect("home")


# Logout view
def logout_user(request):
    """
    Logout View
    To log out user from the system
    """
    logout(request)
    return redirect('login')


@login_required(login_url='login/')
# personal profile page of the users
def profilePage(request):
    """
    This view is for profile page
    of the users, where they can change their 
    password, profile picture, and see items that are assigned to them
    """

    # Get the profile
    profile = Profile.objects.get(owner=request.user)

    # hamdle form for updating the profile picture
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            print("It is valid")
            form.save()
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, error)

    context = {
        'title': 'Profile',
        'profile': profile,
        'items': ItemAssignment.objects.filter(requestor=request.user, status='out'),
        'form': ProfileForm(instance=profile)
    }
    return render(request, 'profile.html', context)


@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
# Page to generate and print reports about the items
def reportPage(request):
    """
    View to generate the report, by using custom filter
    and print or download it in different formats
    such as csv, xls, pdf.

    """

    # get the department
    department = Department.objects.filter(head=request.user).first()
    items = Item.objects.filter(department=department)

    # filter queries
    category = request.GET.get("category")
    owner = request.GET.get("owner")
    status = request.GET.get("status")
    item_type = request.GET.get("item_type")
    date_received = request.GET.get("date_recieved")
    date_received_to = request.GET.get("date_recieved_to")

    # save in dictionary to pass to the page
    search_filters = {
        "category": category if category is not None else "",
        "owner": owner if owner is not None else "",
        "status": status if status is not None else "",
        "item_type": item_type if item_type is not None else "",
        "date_recieved": date_received if date_received is not None else "",
        "date_recieved_to": date_received_to if date_received_to is not None else "",
    }

    # filtering items
    items_list = items.filter(
        Q(category__name__contains=search_filters["category"]) &
        Q(status__contains=search_filters["status"]) &
        Q(item_type__contains=search_filters["item_type"])
    )

    # validation of the fields
    if search_filters["date_recieved"] != "":
        items_list = items_list.filter(
            date_received__gte=search_filters["date_recieved"])

    if search_filters["date_recieved_to"] != "":
        items_list = items_list.filter(
            date_received__lte=search_filters["date_recieved_to"])

    if search_filters["owner"] != "":
        items_list = items_list.filter(
            holder__username__contains=search_filters["owner"])

    # passing data to the page
    context = {
        "title": "reports",
        "items": items_list,
        "categories": Category.objects.filter(department=department),
        "owners": User.objects.all(),
        "search_filters": search_filters
    }
    return render(request, 'report.html', context)


@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def loans(request):

    department = Department.objects.filter(head=request.user).first()
    items = ItemAssignment.objects.filter(department=department, status="out")

    # filter queries
    category = request.GET.get("category")
    owner = request.GET.get("owner")
    date_received = request.GET.get("date_recieved")
    date_received_to = request.GET.get("date_recieved_to")

    # save in dictionary to pass to the page
    search_filters = {
        "category": category if category is not None else "",
        "owner": owner if owner is not None else "",
        "date_recieved": date_received if date_received is not None else "",
        "date_recieved_to": date_received_to if date_received_to is not None else "",
    }

    # filtering items
    items_list = items.filter(
        Q(item__category__name__contains=search_filters["category"])
    )

    # validation of the fields
    if search_filters["date_recieved"] != "":
        items_list = items_list.filter(
            date__contains=search_filters["date_recieved"])

    if search_filters["date_recieved_to"] != "":
        items_list = items_list.filter(
            due_date__contains=search_filters["date_recieved_to"])

    if search_filters["owner"] != "":
        items_list = items_list.filter(
            requestor__username__contains=search_filters["owner"])

    # passing data to the page
    context = {
        "title": "loans",
        "items": items_list,
        "categories": Category.objects.filter(department=department),
        "owners": User.objects.all(),
        "search_filters": search_filters
    }

    return render(request, 'loans.html', context)


@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def categories(request):
    """
    View for adding new categories
    it should be done only by head of the specific department

    """

    department = Department.objects.filter(head=request.user).first()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cateogry = form.save(commit=False)
            cateogry.department = department
            cateogry.save()
            messages.success(request, 'Category added successfully')
            return redirect('categories')

        # if form is not valid show errors
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, error)

    # passing data to the page
    context = {
        'form': CategoryForm(),
        "title": "Categories",
        "categories": Category.objects.filter(department=department),
        'form_url': 'categories',

    }

    return render(request, 'categories.html', context)


@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def categories_update(request, pk):
    """
    View to update category
    """
    category = Category.objects.get(id=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('categories')

        # if form is not valid show errors
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, error)

    context = {
        'form': CategoryForm(instance=category),
        "title": "Update Category",
        "pk": pk
    }

    return render(request, 'categories.html', context)


@login_required(login_url='login/')
@user_passes_test(is_department_head, login_url='profile/')
def categories_delete(request, pk):
    """
    View to remove category from the DB
    """
    category = Category.objects.get(id=pk).delete()
    return redirect('categories')
