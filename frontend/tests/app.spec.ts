import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import { personas, answerQuestion } from './personas';

const logFile = 'test-run.log';
if (fs.existsSync(logFile)) fs.unlinkSync(logFile);

function logTest(message: string) {
    const ts = new Date().toISOString().replace('T', ' ').substring(0, 19);
    const formatted = `[${ts}] [Playwright-E2E] ${message}\n`;
    fs.appendFileSync(logFile, formatted);
    console.log(formatted.trim());
}

const testMatrix = [
    { u1: 'A', u2: 'B' }
];

let globalAnswersReport: any = {};

test.describe('Compatibility Engine Persona Matrix', () => {
    
    test.beforeEach(({ page }) => {
        page.on('console', msg => logTest(`Browser Console [${msg.type()}]: ${msg.text()}`));
        page.on('pageerror', err => logTest(`Browser Error: ${err.message}`));
        page.on('request', req => {
            if (req.url().includes('/api/telemetry')) {
                logTest(`Network [Telemetry POST]: ${req.url()}`);
            }
        });
    });

    for (const pair of testMatrix) {
        test(`Simulate ${pair.u1} & ${pair.u2} match`, async ({ browser }) => {
            test.setTimeout(900000); 
            
            logTest(`Starting matrix test: Persona ${pair.u1} and Persona ${pair.u2}`);
            const context1 = await browser.newContext();
            const page1 = await context1.newPage();
            
            // USER 1
            logTest(`Navigating User 1 (Persona ${pair.u1}) to home page...`);
            await page1.goto('/');
            
            await page1.waitForSelector('text=AI Engine Online', { timeout: 15000 });
            await page1.click('button:has-text("Get Started")');
            logTest(`User 1 clicked Get Started`);
            
            await page1.waitForSelector('text=Generate 1-on-1 Match Link');
            await page1.click('button:has-text("Generate 1-on-1 Match Link")');
            
            await page1.waitForSelector('input[readonly]');
            const shareLinkInput = await page1.locator('input[readonly]').inputValue();
            logTest(`Generated Share Link: ${shareLinkInput}`);
            
            await page1.click('button:has-text("Proceed to Questionnaire")');
            
            // Demographics User
            await page1.waitForSelector('text=Astrological Fingerprint');
            await page1.fill('input[placeholder="Full Name"]', personas[pair.u1].name);
            await page1.fill('input[type="date"]', "1995-05-15");
            await page1.fill('input[type="time"]', "14:30");
            await page1.fill('input[placeholder="City of Birth"]', "Mumbai");
            await page1.click('button:has-text("Start Simulation")');
            logTest(`User 1 (${pair.u1}) filled demographics.`);
            
            // Questionnaire User 1
            logTest(`Starting questionnaire for User 1 (${pair.u1})...`);
            await answerQuestion(page1, personas[pair.u1], logTest);
            logTest(`User 1 finished. Waiting for dashboard/partner screen...`);
            await page1.waitForSelector('text=Waiting for your partner to finish...', { timeout: 15000 });
            
            // USER 2
            logTest(`User 1 is waiting. Now launching User 2 (Persona ${pair.u2}) with link: ${shareLinkInput}`);
            const context2 = await browser.newContext();
            const page2 = await context2.newPage();
            
            let capturedAnswers: any = null;
            page2.on('request', req => {
                if (req.url().includes('/api/onboarding/submit') && req.method() === 'POST') {
                    capturedAnswers = req.postDataJSON();
                    logTest(`Captured final submission payload for pair ${pair.u1}&${pair.u2}`);
                }
            });
            
            await page2.goto(shareLinkInput);
            
            // Demographics User
            await page2.waitForSelector('text=Astrological Fingerprint');
            await page2.fill('input[placeholder="Full Name"]', personas[pair.u2].name);
            await page2.fill('input[type="date"]', "1996-08-20");
            await page2.fill('input[type="time"]', "09:15");
            await page2.fill('input[placeholder="City of Birth"]', "Delhi");
            await page2.click('button:has-text("Start Simulation")');
            logTest(`User 2 (${pair.u2}) filled demographics.`);
            
            // Questionnaire User 2
            logTest(`Starting questionnaire for User 2 (${pair.u2})...`);
            await answerQuestion(page2, personas[pair.u2], logTest);
            
            logTest(`User 2 finished. Waiting for Compatibility Dashboard...`);
            
            await page1.waitForTimeout(2000);
            await page2.waitForTimeout(2000);
            
            await expect(page2.locator('text=Compatibility Dashboard')).toBeVisible({ timeout: 15000 });
            await expect(page1.locator('text=Compatibility Dashboard')).toBeVisible({ timeout: 15000 });
            logTest(`Both users successfully reached the Dashboard!`);
            
            globalAnswersReport[`${pair.u1}_${pair.u2}`] = capturedAnswers;
            
            await context1.close();
            await context2.close();
            logTest(`Test ${pair.u1}&${pair.u2} Passed.`);
        });
    }

    test.afterAll(() => {
        logTest(`All Matrix Tests complete. Writing answers-report.json`);
        fs.writeFileSync('answers-report.json', JSON.stringify(globalAnswersReport, null, 2));
    });
});
