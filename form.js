const express = require('express');
const router = express.Router();
const Entry = require('../models/Entry');
const Item = require('../models/Item');
const nodemailer = require('nodemailer');

// Nodemailer transporter
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

// @route   POST /api/form/submit
// @desc    Submit a new entry
router.post('/submit', async (req, res) => {
  const { fullName, department, mobileNumber, itemTaken, quantity, purpose } = req.body;

  try {
    // 1. Check stock
    const item = await Item.findOne({ name: itemTaken });
    if (!item || item.quantity < quantity) {
      return res.status(400).json({ msg: 'Not enough items in stock.' });
    }

    // 2. Create new entry
    const newEntry = new Entry({
      fullName,
      department,
      mobileNumber,
      itemTaken,
      quantity,
      purpose,
    });
    await newEntry.save();

    // 3. Deduct stock
    item.quantity -= quantity;
    await item.save();

    // 4. Send email notification
    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: process.env.HOD_EMAIL,
      subject: 'New Component Request',
      html: `
        <h3>A new component has been issued:</h3>
        <table border="1" cellpadding="5" cellspacing="0">
          <tr><td><strong>Full Name:</strong></td><td>${fullName}</td></tr>
          <tr><td><strong>Department:</strong></td><td>${department}</td></tr>
          <tr><td><strong>Item Taken:</strong></td><td>${itemTaken}</td></tr>
          <tr><td><strong>Quantity:</strong></td><td>${quantity}</td></tr>
          <tr><td><strong>Purpose:</strong></td><td>${purpose || 'N/A'}</td></tr>
        </table>
      `,
    };
    transporter.sendMail(mailOptions);

    // 5. Send low stock alert if necessary
    if (item.quantity <= 5) { // Low stock threshold
        const lowStockMailOptions = {
            from: process.env.EMAIL_USER,
            to: process.env.HOD_EMAIL, // Or a different admin email
            subject: `Low Stock Alert: ${item.name}`,
            html: `<h3>The quantity for ${item.name} is low. Only ${item.quantity} left.</h3>`,
        };
        transporter.sendMail(lowStockMailOptions);
    }

    res.status(201).json(newEntry);
  } catch (err) {
    res.status(500).send('Server Error');
  }
});

// @route   GET /api/form/items
// @desc    Get all available items for the dropdown
router.get('/items', async (req, res) => {
    try {
        const items = await Item.find({ quantity: { $gt: 0 } }).select('name');
        res.json(items);
    } catch (err) {
        res.status(500).send('Server Error');
    }
});


module.exports = router;
