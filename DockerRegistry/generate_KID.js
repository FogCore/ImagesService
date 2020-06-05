var bluebird = require('bluebird');
var crypto = require('crypto');
var forge = require('node-forge');
var fs = require('fs');

var data = {};

var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

function base32encode(value) {
    var skip = 0;
    var bits = 0;
    var output = '';

    // Iterate over bytes
    var i = 0;
    while (i < value.length) {
        var v = value[i];
        if (typeof v == 'string') {
            v = v.charCodeAt(0);
        }

        // Set current bits
        if (skip < 0) { // We have a carry from the previous byte
            bits |= (v >> (-skip));
        } else { // No carry
            bits = (v << skip) & 248;
        }

        // Produce a character if there is enough data, otherwise, get more data
        if (skip < 4) {
            output += alphabet[bits >> 3];
            skip += 5;
        } else {
            skip -= 8;
            i++;
        }
    }

    // Consume any remaining bits left
    output += (skip < 0 ? alphabet[bits >> 3] : '');
    return output;
}

bluebird.bind(data).then(function() {
    return fs.readFileSync('./certs/token.crt');
}).then(function(crt) {
    this.crt = crt;
}).then(function() {
    var cert = forge.pki.certificateFromPem(this.crt);
    var asn1 = forge.pki.publicKeyToAsn1(cert.publicKey);
    var der = forge.asn1.toDer(asn1);
    var buf = Buffer.from(der.getBytes(), 'binary');
    var hash = crypto.createHash('sha256').update(buf).digest();
    var base32 = base32encode(hash.slice(0, 30));

    // Create key id (fingerprint)
    this.kid = '';
    for (var i = 0; i < 48; ++i) {
        this.kid += base32[i];
        if (i % 4 === 3 && (i + 1) !== 48) {
            this.kid += ":";
        }
    }
    console.log(this.kid);
});
