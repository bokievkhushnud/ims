
// var html5QrcodeScanner = new Html5QrcodeScanner(
// 	"reader", { fps: 10, qrbox: 250 });
let scan = document.getElementById("scanqr")
let stop_scan = document.getElementById("closeqr")
let stop_scan1 = document.getElementById("closeqr1")
const html5QrCode = new Html5Qrcode(/* element id */ "reader");
scan.addEventListener('click', () => {
  // This method will trigger user permissions
  Html5Qrcode.getCameras().then(devices => {
    if (devices && devices.length) {
      console.log(devices.length)
      var cameraId = devices[devices.length - 1].id;
      html5QrCode.start(
        cameraId,
        {
          fps: 10,
          facingMode: "environment",
          // qrbox: { width: 200, height: 200 }  // Optional, if you want bounded box UI
        },
        (decodedText, decodedResult) => {
          html5QrCode.stop().then((ignore) => {
            console.log("QR Code scanning is ")
            // QR Code scanning is stopped.
          }).catch((err) => {
            // Stop failed, handle it.
          });
          window.location = `https://invenotry-ms.herokuapp.com/${decodedText}/`;
        },
        (errorMessage) => {
          // parse error, ignore it.
        })
        .catch((err) => {
          // Start failed, handle it.
        });
    }
  }).catch(err => {
    // handle err
  });

  stop_scan.addEventListener('click', () => {
    html5QrCode.stop().then((ignore) => {
      console.log("QR Code scanning is ")
      // QR Code scanning is stopped.
    }).catch((err) => {
      // Stop failed, handle it.
    });
  })
  stop_scan1.addEventListener('click', () => {
    html5QrCode.stop().then((ignore) => {
      console.log("QR Code scanning is ")
      // QR Code scanning is stopped.
    }).catch((err) => {
      // Stop failed, handle it.
    });
  })

})

// File based scanning
const fileinput = document.getElementById('qr-input-file');
fileinput.addEventListener('change', e => {
  if (e.target.files.length == 0) {
    // No file selected, ignore 
    return;
  }
  const imageFile = e.target.files[0];
  // Scan QR Code
  html5QrCode.scanFile(imageFile, true)
    .then(decodedText => {
      window.location = `http://127.0.0.1:8000/${decodedText}/`;
    })
    .catch(err => {
      // failure, handle it.
      console.log(`Error scanning file. Reason: ${err}`)
    });
});

// Reset Filter

let resetbtn = document.getElementById("reset_filter")
resetbtn.addEventListener("click", (e) => {
  e.preventDefault()
  document.getElementById("date_recieved_filter").value = ""
  document.getElementById("date_recieved_filter1").value = ""
  document.getElementById("cat_select").value = ""
  document.getElementById("owner_select").value = ""
  document.getElementById("item_type").value = ""
  document.getElementById("status_select").value = ""
})

// Select All 
document.getElementById("selectAll").addEventListener("change", function () {
  var options = document.getElementsByClassName("option");
  for (var i = 0; i < options.length; i++) {
    options[i].checked = this.checked;
  }
});

// if any of them is not selected deselect all
var options = document.getElementsByClassName("option");
for (var i = 0; i < options.length; i++) {
  options[i].addEventListener("change", function () {
    var selectAll = document.getElementById("selectAll");
    var allChecked = true;
    for (var j = 0; j < options.length; j++) {
      if (!options[j].checked) {
        allChecked = false;
        break;
      }
    }
    selectAll.checked = allChecked;
  });
}

