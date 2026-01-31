const fs = require('fs');
const path = require('path');
const nodemailer = require('nodemailer');
require('dotenv').config();

const ALERT_FILE = path.join(__dirname, '.last_alert');
const LOG_FILE = path.join(__dirname, 'claim.log');
const ALERT_INTERVAL = 12 * 60 * 60 * 1000; // 12 hours
const TO_EMAIL = process.env.TO_EMAIL || process.env.SMTP_USER; // Use env var or default to sender

async function sendEmail() {
    const type = process.argv[2] || 'failure'; // 'success' or 'failure'

    // 1. Check frequency only for failure
    if (type === 'failure' && fs.existsSync(ALERT_FILE)) {
        const lastAlertTime = parseInt(fs.readFileSync(ALERT_FILE, 'utf8'));
        const now = Date.now();
        if (now - lastAlertTime < ALERT_INTERVAL) {
            console.log('Alert skipped: Too frequent.');
            return;
        }
    }

    // 2. Check SMTP config
    if (!process.env.SMTP_USER || !process.env.SMTP_PASS) {
        console.log('Email skipped: SMTP configuration missing in .env');
        console.log('Please configure SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS in .env file');
        return;
    }

    // 3. Get last few lines of log
    let logContent = 'No log available';
    let logsArray = [];
    if (fs.existsSync(LOG_FILE)) {
        try {
            logsArray = fs.readFileSync(LOG_FILE, 'utf8').split('\n');
            logContent = logsArray.slice(-50).join('\n'); // Last 50 lines
        } catch (e) {
            logContent = `Failed to read log: ${e.message}`;
        }
    }

    // 4. Configure Email Content
    let subject, text;
    if (type === 'success') {
        // Special Logic: Only send email if a game was actually claimed
        // We look for "Claimed successfully" in the logs of the current run (last 100 lines to be safe)
        const recentLogs = logsArray.slice(-100).join('\n');
        const hasClaimed = recentLogs.includes('Claimed successfully');
        
        if (!hasClaimed) {
            console.log('Success email skipped: No new games claimed (Already in library or other status).');
            return;
        }

        subject = '🎁 New Free Game Claimed!';
        text = `The auto-claimer script successfully claimed a new game!\n\nTime: ${new Date().toLocaleString()}\n\nRecent Logs:\n----------------\n${logContent}\n----------------`;
    } else {
        subject = '⚠️ Epic Games Auto-Claimer Alert';
        text = `The auto-claimer script encountered an error.\n\nTime: ${new Date().toLocaleString()}\n\nRecent Logs:\n----------------\n${logContent}\n----------------`;
    }

    // 5. Send Email
    const transporter = nodemailer.createTransport({
        host: process.env.SMTP_HOST || 'smtp.qq.com',
        port: process.env.SMTP_PORT || 465,
        secure: true, // true for 465, false for other ports
        auth: {
            user: process.env.SMTP_USER,
            pass: process.env.SMTP_PASS,
        },
    });

    try {
        const info = await transporter.sendMail({
            from: `"Epic Claimer Bot" <${process.env.SMTP_USER}>`,
            to: TO_EMAIL,
            subject: subject,
            text: text,
        });

        console.log(`${type} email sent:`, info.messageId);
        
        // Update last alert time only for failure to limit frequency
        if (type === 'failure') {
            fs.writeFileSync(ALERT_FILE, Date.now().toString());
        }
    } catch (error) {
        console.error('Failed to send email:', error);
    }
}

sendEmail();
