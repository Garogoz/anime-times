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

// Function to display anime data on the HTML page
function displayAnimeData(animeData) {
    animeData.forEach(anime => {
        const dayColumn = document.getElementById(anime.datetime.weekday);
        if (dayColumn) {
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
            
            dayColumn.appendChild(animeEntry);
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
    });
}


// Call the functions when the page loads
document.addEventListener('DOMContentLoaded', function() {
    sendLocalStorageData();
});
