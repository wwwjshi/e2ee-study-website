// get cookie value by it's key
function getCookie(name) {
    // get all cookie and make it for easier to extract
    const value = `; ${document.cookie}`;
    // split to obtain the particular value
    const parts = value.split(`; ${name}=`);
    // get value only
    if (parts.length === 2) {
        //console.log(parts.pop().split(';').shift())
        return parts.pop().split(';').shift();
    }
}

function downloadKey(filename, value) {    
    // download public key in case local storage is cleared
    var toDownload = document.createElement('a');
    toDownload.href = 'data:attachment/text,' + encodeURI(value);
    toDownload.target = '_blank';
    toDownload.download = filename+'.txt';
    toDownload.click();
}

// public key download button
var btn = document.getElementById("pvk");
btn.onclick = function() { downloadKey("privateKey", localStorage.getItem(getCookie('user')+'_privateKey'))}

// signature key download button
var btn = document.getElementById("sgk");
btn.onclick = function() { downloadKey("signatureKey", localStorage.getItem(getCookie('user')+'_signKey'))}
