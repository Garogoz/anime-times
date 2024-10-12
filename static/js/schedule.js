// Function to send local storage data to the server
function sendLocalStorageData() {
    let animeIds = JSON.parse(localStorage.getItem('animeIds')) || [];

    fetch('/process_local_storage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ animeIds: animeIds }),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        displayAnimeData(data.anime_data)
    })
    .catch(error => console.error('Error:', error));
}

//delete anime if data is null
function deleteAnimeIfnotAiring(animeid) {
    let animeIds = JSON.parse(localStorage.getItem('animeIds')) || [];
    
    // Find the index of the animeid in the array
    const index = animeIds.indexOf(animeid.toString());

    // If the animeid exists in the array, remove it
    if (index !== -1) {
        animeIds.splice(index, 1);

        // Save the updated array back to localStorage
        localStorage.setItem('animeIds', JSON.stringify(animeIds));
    }
}

// Function to display anime data on the HTML page
function displayAnimeData(animeData) {
    //display clear button if there are anime added to schedule
    if (animeData.length > 0) {
        const clearButton = document.getElementById("clearButton");
        clearButton.style.display = "block";
    }
    animeData.forEach(anime => {
        if (anime.nextAiringEpisode !== null) {
            const dayContent = document.getElementById(anime.datetime.weekday);
            if (dayContent) {
                const animeEntry = document.createElement('div');
                const animeInfo = document.createElement('div');
                const animeTitle = document.createElement('div');
                const nextEpisode = document.createElement('div');
                animeEntry.classList.add('anime-entry');
                animeEntry.innerHTML = `<img class='imgschedule'src='${anime.coverImage.large}'>`;

                animeInfo.classList.add('animeInfo');

                animeTitle.classList.add('animeTitle');
                animeTitle.innerHTML= `<h6 class='schedule-text'>${anime.title.romaji}</h6>`;

                nextEpisode.classList.add('next-episode');
                nextEpisode.innerHTML= `<h6 class='schedule-text'>Episode ${anime.nextAiringEpisode.episode}</h6>`;
                
                dayContent.appendChild(animeEntry);
                animeEntry.appendChild(animeInfo);
                animeInfo.appendChild(animeTitle);
                animeInfo.appendChild(nextEpisode);
            

                // Add hover event listeners
                animeEntry.addEventListener('mouseenter', () => {
                    animeTitle.innerHTML = `<h6 class='schedule-text'>${anime.title.english}</h6>`;
                });

                animeEntry.addEventListener('mouseleave', () => {
                    animeTitle.innerHTML = `<h6 class='schedule-text'>${anime.title.romaji}</h6>`;
                });
                
                // Add click event listener to redirect on click
                animeEntry.addEventListener('click', () => {
                    const targetUrl = `/anime/${anime.id}`;
                    window.location.href = targetUrl;
                });
            }
        }
        else {
            deleteAnimeIfnotAiring(anime.id);
        }
    });
}
document.getElementById('search-button').addEventListener('click', function() {
    window.location.href = '/anime';
});

// Call the functions when the page loads
document.addEventListener('DOMContentLoaded', function() {
    sendLocalStorageData();
    
    const headers = document.querySelectorAll('.dayheader');

    headers.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    });
});
