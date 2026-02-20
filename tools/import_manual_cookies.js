const fs = require('fs');
const path = require('path');

// Raw input from user (PowerShell style cookies)
const rawCookies = [
    { name: "EPIC_DEVICE", value: "56160d036358466699f4930e3854d74b", domain: ".epicgames.com" },
    { name: "_tald", value: "c276854b-c56f-4009-a15f-45f889d1eb18", domain: ".epicgames.com" },
    { name: "EPIC_SSO_RM", value: "5b8d98cbe77541abafa63982766d475b", domain: ".epicgames.com" },
    { name: "dfpfpt", value: "e01eb430e95744c2925f7f30426e8ab1", domain: ".epicgames.com" },
    { name: "EPIC_LOGIN_ID", value: "%7B%22loginId%22%3A%2267280095-7e89-47ba-a4de-eb59fcba72fe%22%2C%22created%22%3A1770629648061%7D", domain: ".epicgames.com" },
    { name: "_epicSID", value: "5059b1bf8dde4578b956a3ce09638349", domain: ".epicgames.com" },
    { name: "fptctx2", value: "taBcrIH61PuCVH7eNCyH0HyAAKgSb15ZEqidLg30r8NvkPdNpYKoXjIeJVuwl7w83qdjr19LS9G1wEy5OkHtdB%252fx1fmE7HeJvxsRuzZDttE8cnb7hwZ4dUExwa%252fr2aC22Z59xO0b2Tm5Wf69FyrNDyiquWttnLNFcUNbFTfn%252bdiRdj7DnQ1mLgAU2zLQc9ZjFk%252fqJW2aVeKnDdc2QNfFf3EV3IG2qLEQvYIe41FVaUA2Mq1%252b3AJmM7P%252bqdhtZopd0VW49zUosAGwaQNZYvrMmc1CXIX3LuU5YEF%252fcJrxMwdLVN7C6IH9LBrBQ2W5BneQ1TYahexfR72fMuBo5C7nJ4VTJ9P%252bFuQNO9z8lu0K%252fg8%253d", domain: ".epicgames.com" },
    { name: "EPIC_SSO", value: "5b8d98cbe77541abafa63982766d475b", domain: ".epicgames.com" },
    { name: "EPIC_BEARER_TOKEN", value: "838180f3aa604a0c84c97b094992df69", domain: ".epicgames.com" },
    { name: "bearerTokenHash", value: "12545b00564e2c735615ea47af4853c74d0aaa4d324fa506e1ccd59b83eefa98", domain: ".store.epicgames.com" },
    { name: "EPIC_EG1", value: "eg1~eyJraWQiOiJnX19WS2pTU21xSjB4WmoxUllrTEdLUTdkbkhpTTlNTGhGVndLUHlTREI0IiwiYWxnIjoiUFMyNTYifQ.eyJhcHAiOiJkaWVzZWx3ZWIiLCJzdWIiOiI0ZWE2Mzk0MzA1MmE0ZjBkYWExNTY3MWVmYjk3NGU3ZSIsImR2aWQiOiI1NjE2MGQwMzYzNTg0NjY2OTlmNDkzMGUzODU0ZDc0YiIsIm12ZXIiOmZhbHNlLCJjdHkiOiJDTiIsImNsaWQiOiI4NzVhM2I1N2QzYTY0MGE2YjdmOWI0ZTg4MzQ2M2FiNCIsImRuIjoi6ZqU5aOB546L6Zi_5Y2aIiwiYW0iOiJ0b2tlbl90b190b2tlbiIsInAiOiJlTnFsVnUxdTZqQU1mWitKU1dNRHBsWGlBYTYwWDFmM0JkekVMUlpwVWlVcGpQdjAxMDQvS0xEZGx1MFhEYkVkKy9qNEpMVjN1bEV4cTV2Y2tNcnFkaG0yend2bE5IclVXTldSbk8wTlZnaWJsN2ZWeTlQNkdWYkZrd1pZcmpldlN5enl0OWNWdm1LbVhGTTdHN0xDSTI1ZkZoNFBoTWZlMjJQdGZNd2krQkxqZHNsblZGVmpTWUVjRVRLeUViMEZ3M2FnczRBeGtpM2JYQzdzOEtPekE4WEgyWmhKdE9kRnYrb082NWNQdklXTmdlaEI3VGxndjY4cDFBWk9VSEttRmJMaFZHMGN4MUR1d1ovNkVCU3hDcU9UdTk4d0RWT0ZFVFJFYUxPemthSkpTYlRGMWhDNFNpNTl1UWhOSHBTbml5YU0vM3ZVV0xCVGZkbkhBRmJuN2dOL2x0dzFjR0VIekFqdVRwQVc0NDVDZFA0a0tiT3hjWU9CS3dyMFlmUi9sMVdFMU0zSzZTSFBjNDhOUjV2TnN1Z2d4TzNtVTNReTBnblEweTk5Z2RTWERPRTRvNVQ0a3kyRFU1UUlGdW5Bb2JyTkx3RGhmekRFZ1VpM1BKbXNSNGdZcWNMYnVSc3cxeHg4dTE2VVZNeUhTWHNvb25nSWs2NmFkRVc4WVZ3bWc0NmNwRzhCL1lFVWttVUVySklLN2tvUkRaV1VrMkdRZjRCYkJzYmN5eUVGbmpWb3VTZzhvZFV6eHVKaHUxeC9LVVdLTlN0aVQyaUcrMUw1RE8yUmVmYjVtTmJvS3dxaDVXZ05wOVNQdVdVY3VmUWtmN1huTnFBdHllTEZJR1pwUStZTy9CNGpRNlp3RUREcG1qRWhlNmNEL2tkb3g0SXNQZjlrN0tieE5rRFZZNDRXQ3hMeEYvRkFGbUhsRG5odWVYUTFxYVFIMEZpMTQvUjdUdlJpbXh1bjl1L1M2VW5CWHE0WVRoOHRlcmxhU3AvS3locGh6YlF6ZDZ2eGFnY0J6NEkybHl2Q2xNL3VuRjQ2WndRNEEzQ2J4bDA4UDFMWWlZUGs1UEVJWHM5MmJjMGYrNXZqSjY4Q25lNmlLM0wzeTBsL2FPSk9RYzJvNUEwWlRiWndXZnFxd0ZMQjRwdms3RnUwdkxvaWFtZk1rQjUvdDBOYmtNSFJHMG1XdkhHdldpbU9oeXBsSjJRVzhla243T3FtTEtIQ01INExPRkh3dTRTMWxmM05vdFdIREhSRmR0b3JCOU9wK05WMTBVL2ZWYzBzSHhIL3VEM2E5Tm1JaWZQTUVVWkpZUWpPejI4RUdBeS8wd3RSSnEweGpMSVpzMFZJSkhQeGJkUmxBcHd2bVRKL1d5Vm9RWmw5ODQxOXBWQ05CelN1bG1McEFPbzBQR2RtaWN1dFhDY0VPR1o2UWxTc2pkQmRydklXRkxXOGZWSjFSUGtISjVVUGJ3PT0iLCJpYWkiOiI0ZWE2Mzk0MzA1MmE0ZjBkYWExNTY3MWVmYjk3NGU3ZSIsInNlYyI6MCwiYWNyIjoidXJuOmVwaWM6bG9hOmFhbDEiLCJjbHN2YyI6ImRpZXNlbHdlYiIsInQiOiJzIiwiYXV0aF90aW1lIjoxNzY3NzA1OTY1LCJpYyI6dHJ1ZSwiZXhwIjoxNzcxNDU0NTk2LCJpYXQiOjE3NzE0MjU4MDAsImp0aSI6ImRkM2Q0YTUzOWYzMTRhMTdhMjhjNmY5Mzk0ZDIxZmNlIn0.PHxSGXd5NwqLzmyqYwIeoYdVKWcuGA_rG0H5VkRb1J1WFLVW5bSBvhXvYhAootDtvzcI9XH-Gy3QKcpP_RemRrGUNwDLdiPtsxU4ucKw_6tnVEBdEHB3smOt3n6GhMzXx0LfSf7sWuRLHlUVrzv2JJTpsGEGOWenzTvg13Pky5Zb6wqjAteqkU1_TkDfyKq7XE5szorR-Bf9EyQiILKJPQX7eElJV95QSZAQpF-6rH-LqgufdX5DOZQRpXN0ks3xjQjq5ZgpT4sW1tw8xuCZTEm3Hq9DDMAI5TgJrCbsW8jsCNMKTwu26gf_TB23_3uvOsQF-mO9TSBnWD-cjMH429A3Vf5L_36GBFUTvinPM22Jfnp6GtxRNLjGcfuz2Bs4U57aidarOdh4nYVcnGAn9bg_PUr7-D1Kmoi76kGPhJAkrrug64lhZnWRgmRtGrM-OqXf_3JBB0e2k6fLuiFT8RTp3NgncGFZpJnxkNvwP-krrQyHuxucMf0qSTx77iBFUfVtElbuQ68ifmJniOr-8jZaUWoEygD91I_a6j7X8RPtbx6RqNcRBWyIg82r5N039fuxkd4bJRGlDmAiX9xqpVWCqCxe98ifYO3E4p1pIsi_3nTk1orLSOTYhtCZ8-ka-3_mTKF2LxJtXeJ6kzmC-4TtuFAGzh5FvcG59X_gbOY", domain: ".epicgames.com" },
    { name: "REFRESH_EPIC_EG1", value: "eg1~eyJraWQiOiJnX19WS2pTU21xSjB4WmoxUllrTEdLUTdkbkhpTTlNTGhGVndLUHlTREI0IiwiYWxnIjoiUFMyNTYifQ.eyJzdWIiOiI0ZWE2Mzk0MzA1MmE0ZjBkYWExNTY3MWVmYjk3NGU3ZSIsImR2aWQiOiI1NjE2MGQwMzYzNTg0NjY2OTlmNDkzMGUzODU0ZDc0YiIsInQiOiJyIiwiY2xpZCI6Ijg3NWEzYjU3ZDNhNjQwYTZiN2Y5YjRlODgzNDYzYWI0IiwiZXhwIjoxODAyOTY1ODAwLCJhbSI6InRva2VuX3RvX3Rva2VuIiwianRpIjoiZjBhN2U3Mzc4YjU3NDRhNjhmOTJkMjNiNjA1Y2ViNzcifQ.Pi96WkYA0Rryn8R4TXOQC76tYBlwUmSzvUhyaihcHRJvc8Fo2reJ-eMYcHv52WMCnXpYrIu-XBtWarhUrp4FNxAuNHJSO7hshTzUXHolcZAXpqN13WyqCKvfRvFtBhZTwu2faSKDX4jqIkCcG0MuDpWp9JfUjxKTONdhJZrNFlUGBfe0SieUxiXeI23_HagUYRct_Vz0vr9jwysvDG1IUDmY419ZoXEvUtFER3oDYd9pGY0o-4GNAIzsahJRiLSSyf68mqOFv5V1EHyOQ8P1kQ5GC28R33-srOgsIsrer4NxnfUc_KSuchY3XL2b2YhfiyQcjGnnDCcuhIkzTKQj6fdfQBzhweT2wt3qUTT8cXG2b3s35nD6mKmLeSIAJE_iPfMqy-ZaWK2jE5ukBkSPeki9rUGZi5q5MQeQFLtahXnaIXsH2yrwE9BQ2VeFCcXIAqifq47XFJFRCUlsCKl-7wAMP25z0IGqcB_V3FVL1Zmn18aFJ_OAhEN4zCI-BdBJMkmob6RK71RObDK6xODww6vPnUjpEHMfhHDewxbY1BXVnXYRMPQrVwrvV5zCPveJdb3FydCuyi3NE8smquL8sRjtOb0jsHdrnr4rc5ns3J8XYLZR_gqSETnHTDNUqulC9uR-wrwfPDcJtoFyN-uEr1UtNWX9eoYLqRan_GFCihk", domain: ".store.epicgames.com" },
    { name: "refreshTokenExpires", value: "2027-02-18T15%3A50%3A00.317Z", domain: ".store.epicgames.com" },
    { name: "storeTokenExpires", value: "2026-02-18T22%3A43%3A16.315Z", domain: ".store.epicgames.com" },
    { name: "cf_clearance", value: "R5T2ABerrFxYpKxvZmN5PZycn_Sfb43YMbCK0n2hiys-1771425832-1.2.1.1-ul3GqnDzhD8ruxufJAElNEFYUxDD11bMWszuW4_s009KbwTv8C6PWIq9MM1yWBC.d0DsIvgZXoIpajrIJ3Qht6s18bl8.uEhoTbg7_0vShVvgM4AFDZWnHdqTQbjfVcRN.o8CawOgy0Lmg1L_5IeEWpulW9BHNbrUSycXrRwuc8bOw45zJ9KfmWX.CC1O0wbc_rr9Fj_1_KsZxB1fGJZMiWvSUPyWWRls96klvmBiaE", domain: ".store.epicgames.com" },
    { name: "__cf_bm", value: "kZtJJPrzv8WvNLpmkk1ERyTPj1c78AdEW_ulANz74Os-1771425861-1.0.1.1-mJCLeTsdk5w1o4lFhvdlSmOnyeXSuum87_4ofU__beS0xEDkGMpbFAj7NJ0XAhsCOvSD8Y0gvevMljN3dKHGj6s3LWJrRblyKgMr5gSGof4", domain: ".store.epicgames.com" }
];

// Convert to Playwright format
const playwrightCookies = rawCookies.map(c => ({
    name: c.name,
    value: c.value,
    domain: c.domain,
    path: "/",
    secure: true,
    httpOnly: false, // Defaulting to false as we don't have this info, but Playwright handles it
    sameSite: "None" // Important for cross-site auth
}));

const outputPath = path.resolve(__dirname, '../claimer/data/cookies.json');
const dataDir = path.dirname(outputPath);

if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
}

fs.writeFileSync(outputPath, JSON.stringify(playwrightCookies, null, 2));
console.log(`Successfully wrote ${playwrightCookies.length} cookies to ${outputPath}`);
