// get cookie value by it's key
function getCookie(name) {
    // get all cookie
    const value = `; ${document.cookie}`;
    // split to obtain the particular value
    const parts = value.split(`; ${name}=`);
    // get value only
    if (parts.length === 2) {
        //console.log(parts.pop().split(';').shift())
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


// base 64 encoded keys
var pbk = document.getElementById("pbk").textContent;
var sgk = localStorage.getItem(getCookie("user")+'_signKey');
console.log(pbk);
console.log(sgk);




// -------------------------ENC-----------------------------------------------------------
// import public key
function getPublicKey(pbk) {
    var key = window.crypto.subtle.importKey(
        "spki",
        b64ToArrBuffer(pbk),
        {
            name: "RSA-OAEP",
            hash: {name: "SHA-256"}
        },
        false,
        ["encrypt"]
    );
    return key;
};

// function enc msg
function encMsg(publicKey, encodeMsg) {
    return window.crypto.subtle.encrypt( 
        {
            name: "RSA-OAEP",
        },
        publicKey,
        encodeMsg
    )
};
//------------------------------------------------------------------------

//--------------------SIGN-------------------------------------------------
// import sign key
function getSignKey(sgk) {
    var key = window.crypto.subtle.importKey(
        "pkcs8",
        b64ToArrBuffer(sgk),
        {
            name: "RSA-PSS",
            hash: {name: "SHA-256"}
        },
        false,
        ["sign"]
    );
    return key;
};

// sign msg
function signMsg(signKey, encryptMsg) {
    return window.crypto.subtle.sign( 
        {
            name: "RSA-PSS",
            saltLength: 128,
        },
        signKey,
        encryptMsg
    )
};

//-----------------------------------------------------------------------





// getting user msg, encrypy and send
async function send_cipher(pbk, sgk) {
    var msg = document.getElementById("msg").value;
    // no input
    if(msg == null || msg ==""){
        console.log("Null input");
        return;
    }

    // encode msg as array buffer for enc
    var encodedMsg = b64ToArrBuffer(window.btoa(msg));

    // encr
    var publicKey = await getPublicKey(pbk);
    console.log(publicKey);
    var encryptMsg = await encMsg(publicKey, encodedMsg);
    encryptMsg = new Uint8Array(encryptMsg);
    console.log(encryptMsg);

    // sign
    var signKey = await getSignKey(sgk);
    console.log(signKey);
    var signature = await signMsg(signKey, encryptMsg);
    signature = new Uint8Array(signature);
    console.log(signature);

    // let decoder = new TextDecoder();
    // var strCipher = decoder.decode(encryptMsg);
    // var strSign = decoder.decode(signature);
    var strCipher = arrayBufferToBase64(encryptMsg);
    var strSign = arrayBufferToBase64(signature);
    console.log(strCipher);
    console.log(strSign);

    // send to server
    var cipher = document.getElementById("cipher");
    cipher.value = strCipher;
    var sign = document.getElementById("sign");
    sign.value = strSign;


    var send = document.getElementById("send");
    send.click();
};









// get msg on click button
var btn = document.getElementById("btn");
btn.onclick = function() {send_cipher(pbk, sgk)};

//let msg = window.prompt()
//console.log("msg: " + document.getElementById("msg").textContent);