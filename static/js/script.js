document.addEventListener("DOMContentLoaded", function (event) {

    console.log("DOM fully loaded and parsed");

    const buttons = document.querySelectorAll('.addbutton');

    // Function to check if ID is in local storage array
    function isIdInLocalStorageArray(id) {
        // Retrieve the array from local storage
        let animeIds = JSON.parse(localStorage.getItem('animeIds')) || [];
        // Check if the ID is in the array
        return animeIds.includes(id);
    }
    
     // Initialize button colors based on local storage
     buttons.forEach(button => {
        const animeId = button.getAttribute('data-anime-id');
        if (!isIdInLocalStorageArray(animeId)) {
            button.innerHTML = "Add"
            button.classList.add('greenbutton');
            button.setAttribute("title", "Click to Add to Schedule");
        } else {
            button.innerHTML = "Remove"
            button.classList.remove('greenbutton');
            button.classList.add('redbutton');
            button.setAttribute("title", "Click to remove from Schedule");
        }
    });

    // Add event listener to each button
    buttons.forEach(button => {
        button.addEventListener('click', function(event) {
            // Prevent the default action of the anchor element
            event.preventDefault();
            event.stopPropagation();

            // Get the anime ID from the button's data attribute
            const animeId = this.getAttribute('data-anime-id');

            // Retrieve the existing array from local storage or create a new one if it doesn't exist
            let animeIds = JSON.parse(localStorage.getItem('animeIds')) || [];
            

             // Check if the ID is already in the array
             if (animeIds.includes(animeId)) {
                // Remove the ID from the array
                animeIds = animeIds.filter(id => id !== animeId);
                // Change classes
                this.classList.remove('redbutton');
                this.classList.add('greenbutton');
                this.innerHTML = "Add"
                this.setAttribute("title", "Click to Add to Schedule")
                console.log("removed");
            } else {
                // Add the new ID to the array
                animeIds.push(animeId);
                this.innerHTML = "Remove"
                this.classList.add('redbutton');
                this.classList.remove('greenbutton');
                this.setAttribute("title", "Click to remove from Schedule");
                console.log("saved");
            }

            // Save the updated array back to local storage
            localStorage.setItem('animeIds', JSON.stringify(animeIds));
        });
    });

    // Function to clear local storage and reset buttons
    function clearLocalStorage() {
        // Clear the array from local storage
        localStorage.removeItem('animeIds');
        console.log("Cleared local storage");
        // Reload the page to reset all states
        location.reload();

        // Reset the buttons to their initial state
        buttons.forEach(button => {
            button.innerHTML = "Add";
            button.classList.add('greenbutton');
            button.setAttribute('title', 'Click to add to Schedule');
            button.classList.remove('redbutton');
        });
    }

    // Get the clear button and attach event listener
    const clearButton = document.getElementById('clearButton');
    
    if(clearButton) {
    clearButton.addEventListener('click', function(event) {
        event.preventDefault();
         // Show a confirmation dialog
         const userConfirmed = window.confirm("Are you sure you want to clear all the Schedule?");
         if (userConfirmed) {
             clearLocalStorage();
         }
    });
}
});
