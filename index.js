const puppeteer = require("puppeteer-extra");
const stealthPlugin = require("puppeteer-extra-plugin-stealth");
const fs = require('fs').promises;

puppeteer.use(stealthPlugin());

// Set the game ID and construct the URL for reviews
const gameId = 291550;
const urlTemplate = `https://steamcommunity.com/app/${gameId}/reviews/?p=1&browsefilter=mostrecent&filterLanguage=english`;

async function givePage() {
    const browser = await puppeteer.launch({
        headless: false,
    });

    const page = await browser.newPage();
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    );

    // Set the language header to ensure English content
    await page.setExtraHTTPHeaders({
        'Accept-Language': 'en-US,en;q=0.9'
    });

    await page.goto(urlTemplate);
    await page.setViewport({ width: 1366, height: 768 });

    return [browser, page];
}

async function scrapeReviews(page) {
    const reviews = [];
    const steamIdsSet = new Set();
    const maxScrollAttempts = 5;

    try {
        let lastPosition = await getScrollPosition(page);
        let running = true;

        while (running) {
            // Select all review cards on the page
            const cards = await page.$$('.apphub_Card');

            // Process the last 20 cards to avoid duplicates
            for (const card of cards.slice(-20)) {
                const steamId = await getSteamId(card);
                if (steamIdsSet.has(steamId)) continue;

                const review = await scrapeReviewData(card);
                reviews.push(review);
                steamIdsSet.add(steamId);
            }

            // Attempt to scroll and load more reviews
            let scrollAttempt = 0;
            while (scrollAttempt < maxScrollAttempts) {
                await scrollToBottom(page);
                const currPosition = await getScrollPosition(page);

                if (currPosition === lastPosition) {
                    scrollAttempt++;
                    await page.waitForTimeout(3000);

                    // If we've tried scrolling 3 times without progress, stop
                    if (scrollAttempt >= 3) {
                        running = false;
                        break;
                    }
                } else {
                    lastPosition = currPosition;
                    break;
                }
            }
        }
    } catch (e) {
        console.error(e);
    }

    return reviews;
}

// Get the current scroll position of the page
async function getScrollPosition(page) {
    return page.evaluate(() => window.scrollY);
}

// Scroll to the bottom of the page
async function scrollToBottom(page) {
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    await page.waitForTimeout(1000);
}

// Extract the Steam ID from the review card
async function getSteamId(card) {
    const profileUrl = await card.$eval('.apphub_friend_block div a:nth-child(2)', el => el.href);
    return profileUrl.split('/').slice(-2)[0];
}

// Scrape relevant data from a review card
async function scrapeReviewData(card) {
    const datePosted = await card.$eval('.apphub_CardTextContent .date_posted', el => el.textContent.trim());
    const earlyAccessReview = await card.$eval('.apphub_CardTextContent .early_access_review', el => el.textContent.trim());

    let receivedCompensation = '';
    try {
        receivedCompensation = await card.$eval('.received_compensation', el => el.textContent);
    } catch (error) {
    }

    // Extract and clean the review content
    let reviewContent = await card.$eval('.apphub_CardTextContent', el => el.textContent.trim());
    [datePosted, earlyAccessReview, receivedCompensation].forEach(text => {
        reviewContent = reviewContent.replace(text, '');
    });
    reviewContent = reviewContent.replace(/\n/g, '');

    const reviewLength = reviewContent.replace(/\s/g, '').length;

    const thumbText = await card.$eval('.reviewInfo div:nth-child(2)', el => el.textContent);
    const playHours = await card.$eval('.reviewInfo div:nth-child(3)', el => el.textContent);

    return { earlyAccessReview, reviewContent, thumbText, reviewLength, playHours };
}

async function run() {
    const arr = await givePage();
    const page = arr[1];
    const reviews = await scrapeReviews(page);
    
    // Convert the reviews array to a JSON string
    const jsonData = JSON.stringify(reviews, null, 2);
    
    // Write the JSON data to a file
    try {
        await fs.writeFile('steam_reviews.json', jsonData);
        console.log('Reviews have been saved to steam_reviews.json');
    } catch (error) {
        console.error('Error writing to file:', error);
    }
    
    console.log(`Scraped ${reviews.length} reviews.`);
    await arr[0].close();
}

run();