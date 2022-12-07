// get cookie value by it's key
function getCookie(name) {
    // get all cookie
    const value = `; ${document.cookie}`;
    // split to obtain the particular value
    const parts = value.split(`; ${name}=`);
    // get value only
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
}

// array buffer to base 64 string
function arrayBufferToBase64(arrayBuffer) {
    var byteArray = new Uint8Array(arrayBuffer);
    var byteString = '';
    for(var i=0; i < byteArray.byteLength; i++) {
        byteString += String.fromCharCode(byteArray[i]);
    }
    var b64 = window.btoa(byteString);

    return b64;
}

// base 64 encoded string to array buffer
function b64ToArrBuffer(b64) {
    var byteStr = window.atob(b64);
    var byteArr = new Uint8Array(byteStr.length);
    for(var i=0; i < byteStr.length; i++) {
        byteArr[i] = byteStr.charCodeAt(i);
    }
    return byteArr;
};


// import private key
// base 64 encoded keys
var pvk = localStorage.getItem(getCookie("user")+'_privateKey');

function getPrivateKey(pvk) {
    var key = window.crypto.subtle.importKey(
        "pkcs8",
        b64ToArrBuffer(pvk),
        {
            name: "RSA-OAEP",
            hash: {name: "SHA-256"}
        },
        true,
        ["decrypt"]
    );
    return key;
};


// dec msg
function decMsg(privateKey, encodeMsg) {
    console.log(privateKey);
    console.log(encodeMsg);
    return window.crypto.subtle.decrypt( 
        {
            name: "RSA-OAEP",
        },
        privateKey,
        encodeMsg
    )
};


function getVerifyKey(vfk) {
    var key = window.crypto.subtle.importKey(
        "spki",
        b64ToArrBuffer(vfk),
        {
            name: "RSA-PSS",
            hash: {name: "SHA-256"}
        },
        false,
        ["verify"]
    );
    return key;
};

function verifyMsg(verifyKey, msg, signature) {
    return window.crypto.subtle.verify( 
        {
            name: "RSA-PSS",
            saltLength: 128,
        },
        verifyKey,
        signature,
        msg
    )
};


async function verifyAndDecr(vfk, cipher, signature, plain){
    //---------------------------------------------
    // verify
    var verifyKey = await getVerifyKey(vfk);
    var isMsg = await verifyMsg(verifyKey, cipher, signature);
    console.log(isMsg);
    if(isMsg === false) {
        plain.textContent =  'Message been Tampered';
        return
    }

    //---------------------------------------------------
    // decrpyt
    var privateKey = await getPrivateKey(pvk);
    console.log(privateKey);
    console.log(cipher);
    var decryptMsg = await decMsg(privateKey, cipher);
    decryptMsg = new Uint8Array(decryptMsg);
    console.log(decryptMsg);
    var strDecMsg = window.atob(arrayBufferToBase64(decryptMsg))
    console.log(strDecMsg);
    plain.textContent = strDecMsg;
    //---------------------------------------------------
}

    

var ciphers = document.getElementsByClassName("cipher");
var signs = document.getElementsByClassName("sign");
var vfks = document.getElementsByClassName("vfk");
var plains = document.getElementsByClassName("plain")
for(var i=0; i < ciphers.length; i++) {
    var cipher = b64ToArrBuffer(ciphers[i].textContent);
    var sign = b64ToArrBuffer(signs[i].textContent);
    var vfk = vfks[i].textContent;
    var plain = plains[i];
    verifyAndDecr(vfk, cipher, sign, plain);
    //plains[i].textContent = verifyAndDecr(vfk, cipher, sign, plain);
}