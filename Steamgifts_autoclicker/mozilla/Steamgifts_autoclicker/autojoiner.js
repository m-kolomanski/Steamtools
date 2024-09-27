// SETUP //
const sync_store = browser.storage.sync;

// check if sync storage is setup correctly
sync_store.get('whitelist').then((res) => {
    if (!Array.isArray(res.whitelist)) {
        sync_store.set({whitelist: [] });
    }
});

// ADDING GAMES TO WHITELIST //
/**
 * Adds an event listener to the "Enter" button for adding a game to the whitelist.
 * The button is selected using the `.sidebar__entry-insert` class. When clicked, 
 * the name of the game (from an element with the `.featured__heading__medium` class) 
 * is retrieved and passed to the `addGameToWhitelist` function.
 */
const enter_button = document.querySelector(".sidebar__entry-insert");
if (enter_button) {
    enter_button.addEventListener('click', () => {
        const entered_name = window.location.pathname.split('/').at(-1);
        addGameToWhitelist(entered_name);
    });
}

/**
 * Checks if the game name is already in the whitelist. If not, adds it to the whitelist.
 * @param {string} game_name - name of the game to be added to whitelist
 */
addGameToWhitelist = async function(game_name) {
    const whitelist = await sync_store.get('whitelist');
    
    if (!whitelist.whitelist.includes(game_name)) {
        let new_whitelist = whitelist.whitelist;
        new_whitelist.push(game_name);
        sync_store.set({ whitelist: new_whitelist }).then(() => {
            // TODO: show some notification
            console.log("game added");
        });
    }
}

// SCANNING FOR GAMES TO JOIN //
// TODO: make sure we do not fetch data on every page
sync_store.get('whitelist').then((res) => {
    const current_whitelist = res.whitelist;
    const giveaways_on_page = document.querySelectorAll("a.giveaway__heading__name");

    let giveaways_to_join = [];

    giveaways_on_page.forEach((giveaway) => {
        const game_name = giveaway.href.split('/').at(-1);

        // check if game is on whitelist //
        if (current_whitelist.includes(game_name)) {

            // check if game is not already joined //
            if (!giveaway.parentElement.parentElement.parentElement.classList.contains('is-faded')) {
                giveaways_to_join.push(giveaway.href);
            }
           
        }
    });

    const n_giveaways = giveaways_to_join.length;
    if (n_giveaways > 0) {
        const sidebar = document.querySelector(".sidebar");

        // consctruct notification //
        const notification = document.createElement("div");
        notification.classList.add("autojoiner-container");
        notification.innerHTML = `
            <p>Detected ${n_giveaways} whitelisted giveaway${n_giveaways > 1 ? "s" : ""}.</p>
            <button
                id="autojoiner-button"
                class="sidebar__entry-insert"
            >Autojoin</button>
        `;

        // trigger autojoining when user confirms //
        notification.querySelector("#autojoiner-button").addEventListener('click', () => {
            notification.innerHTML = `<p>Joining...</p>`;
            autojoinGiveaways(giveaways_to_join);
        });

        sidebar.appendChild(notification);
    }
});


// AUTOJOINING GIVEAWAYS //
/**
 * Function responsible for joining the giveaways. It gathers xsrf token from logout button
 * and extracts giveaway code from the link. Then for each link fires `sendEntryRequest` function.
 * When everything is done, reloads the page.
 * @param {Array} links array containing links for giveaways to join 
 */
const autojoinGiveaways = async function(links) {
    const token = document.querySelector(".js__logout").getAttribute("data-form").split("=").at(-1)

    for (let link of links) {
        await sendEntryRequest(
            token,
            link.split('/').at(-2)
        )
    }

    // added delay before loading page to account for server processing joins //
    setTimeout(() => {
        location.reload();
    }, 1000);
}
/**
 * Sends POST request to the Steamgifts API to join the giveaway.
 * @param {String} xsrf authentication token for steamgifts session.
 * @param {String} code code of the giveaway to join.
 */
const sendEntryRequest = async function(xsrf, code) {
    fetch("https://www.steamgifts.com/ajax.php", {
        method : "POST",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With' : 'XMLHttpRequest',
            'Accept' : "application/json, text/javascript, */*; q=0.01"
        },
        body: new URLSearchParams({
            xsrf_token: xsrf,
            do : "entry_insert",
            code : code
        }).toString()}
    )
}

