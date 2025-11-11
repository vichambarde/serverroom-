const express = require('express');
const router = express.Router();
const Entry = require('../models/Entry');
const Item = require('../models/Item');
const exceljs = require('exceljs');

// Basic Authentication Middleware
const auth = (req, res, next) => {
    const { username, password } = req.body;
    if (username === process.env.ADMIN_USERNAME && password === process.env.ADMIN_PASSWORD) {
        next();
    } else {
        // For GET requests, check headers
        const b64auth = (req.headers.authorization || '').split(' ')[1] || ''
        const [user, pass] = Buffer.from(b64auth, 'base64').toString().split(':')
        if (user === process.env.ADMIN_USERNAME && pass === process.env.ADMIN_PASSWORD) {
            return next()
        }
        res.status(401).send('Authentication failed');
    }
};

// @route   POST /api/admin/login
// @desc    Admin login
router.post('/login', auth, (req, res) => {
  res.json({ msg: 'Login successful' });
});

// @route   GET /api/admin/entries
// @desc    Get all entries with filtering
router.get('/entries', (req, res) => {
    // A more secure implementation would use a token-based auth middleware here
    // For simplicity, this endpoint is kept open for this example.
    const { department, item, startDate, endDate } = req.query;
    let filters = {};
    if (department) filters.department = department;
    if (item) filters.itemTaken = item;
    if (startDate && endDate) {
        filters.timestamp = { $gte: new Date(startDate), $lte: new Date(endDate) };
    }

    Entry.find(filters).sort({ timestamp: -1 })
        .then(entries => res.json(entries))
        .catch(() => res.status(500).send('Server Error'));
});

// @route   GET /api/admin/export
// @desc    Export entries to Excel
router.get('/export', async (req, res) => {
    const entries = await Entry.find().sort({ timestamp: -1 });

    const workbook = new exceljs.Workbook();
    const worksheet = workbook.addWorksheet('Entries');
    worksheet.columns = [
        { header: 'Full Name', key: 'fullName', width: 20 },
        { header: 'Department', key: 'department', width: 15 },
        { header: 'Mobile Number', key: 'mobileNumber', width: 15 },
        { header: 'Item Taken', key: 'itemTaken', width: 15 },
        { header: 'Quantity', key: 'quantity', width: 10 },
        { header: 'Date & Time', key: 'timestamp', width: 20 },
        { header: 'Purpose', key: 'purpose', width: 30 },
    ];
    worksheet.addRows(entries);

    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', 'attachment; filename="entries.xlsx"');
    await workbook.xlsx.write(res);
    res.end();
});

// @route   POST /api/admin/items
// @desc    Add or update an item's stock
router.post('/items', async (req, res) => {
    // Secure this route with proper admin auth
    const { name, quantity } = req.body;
    try {
        let item = await Item.findOne({ name });
        if (item) {
            item.quantity += quantity;
        } else {
            item = new Item({ name, quantity });
        }
        await item.save();
        res.json(item);
    } catch (err) {
        res.status(500).send('Server Error');
    }
});


module.exports = router;
