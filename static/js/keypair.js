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


// get cookie value by it's key
function getCookie(name) {
    // get all cookie
    const value = `; ${document.cookie}`;
    console.log(value);
    // split to obtain the particular value
    const parts = value.split(`; ${name}=`);
    // get value only
    console.log(parts)
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
}


// generate PKE key pair
function generateEncKey() {
    // generate a keyPair
    window.crypto.subtle.generateKey(
        {
            name: "RSA-OAEP",
            modulusLength: 2048,
            publicExponent: new Uint8Array([1, 0, 1]),
            hash: "SHA-256"
        },
        true,
        ["encrypt", "decrypt"]
    )
    .then(function(keyPair){
        // save private key locally
        window.crypto.subtle.exportKey(
            "pkcs8",
            keyPair.privateKey
        ).then(function(exportedPrivateKey) {
            // converting exported private key to String
            var pvk = arrayBufferToBase64(exportedPrivateKey);
            console.log(getCookie('user'));
            filename = getCookie('user')+'_privateKey';

            // store in localStorage
            localStorage.setItem(filename, pvk);

        }).catch(function(err) {
            console.log(err);
        });

        // export public key to server
        window.crypto.subtle.exportKey(
            "spki",
            keyPair.publicKey
        ).then(function(exportedPublicKey) {
            // converting key to string
            var pbk = arrayBufferToBase64(exportedPublicKey)
            //console.log(pbk); // quick check
            document.getElementById('publickey').value = pbk;

        }).catch(function(err) {
            console.log(err);
        });
    })
}


// generate Signature key pair
function generateSignKey() {
    // generate a keyPair
    window.crypto.subtle.generateKey(
        {
            name: "RSA-PSS",
            modulusLength: 2048, 
            publicExponent: new Uint8Array([1, 0, 1]),
            hash: {name: "SHA-256"},
        },
        true,
        ["sign", "verify"]
    )
    .then(function(keyPair){
        // save private/signature key locally
        window.crypto.subtle.exportKey(
            "pkcs8",
            keyPair.privateKey
        ).then(function(exportedPrivateKey) {
            // converting exported private key to String
            var sgk = arrayBufferToBase64(exportedPrivateKey);
            console.log(getCookie('user'));
            filename = getCookie('user')+'_signKey';
            console.log("Signature: "+sgk);
            // store in localStorage
            localStorage.setItem(filename, sgk);

        }).catch(function(err) {
            console.log(err);
        });

        // export public key to server
        window.crypto.subtle.exportKey(
            "spki",
            keyPair.publicKey
        ).then(function(exportedPublicKey) {
            // converting key to string
            var vfk = arrayBufferToBase64(exportedPublicKey)
            document.getElementById('verifykey').value = vfk;
            console.log("Verify: "+vfk);
        }).catch(function(err) {
            console.log(err);
        });


    })
}



generateEncKey();
generateSignKey();