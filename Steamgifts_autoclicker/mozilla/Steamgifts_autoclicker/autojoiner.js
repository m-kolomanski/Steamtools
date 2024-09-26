// SETUP //
const sync_store = browser.storage.sync;

// check if sync storage is setup correctly
sync_store.get('whitelist').then((res) => {
    if (!Array.isArray(res.whitelist)) {
        console.log('setting up storage')
        sync_store.set({whitelist: [] });
    } else {
        console.log("storage setup")
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
