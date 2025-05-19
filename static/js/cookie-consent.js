document.addEventListener('DOMContentLoaded', function() {
    // Check if user has already made a choice
    if (!getCookie('cookie_consent')) {
        showCookieConsent();
    }
    
    // Set up event listeners for the buttons
    const acceptBtn = document.getElementById('cookie-consent-accept');
    const declineBtn = document.getElementById('cookie-consent-decline');
    const settingsBtn = document.getElementById('cookie-consent-settings');
    
    if (acceptBtn) {
        acceptBtn.addEventListener('click', function() {
            setCookie('cookie_consent', 'accepted', 365);
            hideCookieConsent();
            // Here you can initialize analytics or other tracking scripts
            console.log('Cookies accepted');
        });
    }
    
    if (declineBtn) {
        declineBtn.addEventListener('click', function() {
            setCookie('cookie_consent', 'declined', 30);
            hideCookieConsent();
            // Here you can disable any non-essential cookies that were already set
            console.log('Cookies declined');
        });
    }
    
    if (settingsBtn) {
        settingsBtn.addEventListener('click', function() {
            // Here you could show a more detailed settings modal
            alert('Cookie settings would be shown here. For now, you can accept or decline all.');
        });
    }
});

function showCookieConsent() {
    const banner = document.getElementById('cookie-consent-banner');
    if (banner) {
        banner.style.display = 'block';
        // Add a class after a short delay to enable the animation
        setTimeout(() => {
            banner.style.opacity = '1';
            banner.style.transform = 'translateY(0)';
        }, 100);
    }
}

function hideCookieConsent() {
    const banner = document.getElementById('cookie-consent-banner');
    if (banner) {
        banner.style.opacity = '0';
        banner.style.transform = 'translateY(100%)';
        // Remove the banner from the DOM after the animation completes
        setTimeout(() => {
            banner.style.display = 'none';
        }, 300);
    }
}

// Cookie helper functions
function setCookie(name, value, days) {
    let expires = '';
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + (value || '') + expires + '; path=/';
}

function getCookie(name) {
    const nameEQ = name + '=';
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// Expose functions to the global scope for potential use in other scripts
window.CookieConsent = {
    show: showCookieConsent,
    hide: hideCookieConsent,
    getConsent: function() {
        return getCookie('cookie_consent');
    }
};
