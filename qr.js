const qrcode = require('qrcode');
const fs = require('fs');

const url = 'http://localhost:3000'; // Change to your deployed frontend URL

qrcode.toFile('./form_qr_code.png', url, (err) => {
  if (err) throw err;
  console.log('QR code generated successfully!');
});
