function createPlaylistCard(playlist, user_id, redirect_to_edit=true) {
    const playlistContainer = document.createElement('div');
    playlistContainer.classList.add('pure-u-1', 'pure-u-md-1-3', 'pure-u-lg-1-5', 'playlist-container');

    const button = document.createElement('button');
    button.classList.add('playlist');
    if (redirect_to_edit && (playlist.user_id === user_id)){
        button.onclick = function() {  // redirect to edit playlist page
            redirectToEdit(playlist.id);
        }; 
    }
    else{
        button.onclick = function() {
            redirectToViewPlaylist(playlist.id);
        };
    }

    const playlistIcon = document.createElement('div');
    playlistIcon.classList.add('playlist-icon');
    const image = document.createElement('img');
    image.src = playlist.image;
    image.alt = 'Playlist Image';
    playlistIcon.appendChild(image);
    button.appendChild(playlistIcon);

    const playlistName = document.createElement('div');
    playlistName.classList.add('playlist-name');
    playlistName.textContent = playlist.name;
    button.appendChild(playlistName);

    const playlistRating = document.createElement('div');
    playlistRating.classList.add('playlist-rating');
    playlistRating.textContent = playlist.rating;
    button.appendChild(playlistRating);

    const tagsContainer = document.createElement('div');
    tagsContainer.classList.add('pure-g', 'playlist-tags');
    playlist.tags.forEach(tag => {
        const tagElement = document.createElement('div');
        tagElement.classList.add('tag', 'pure-u-1-3');
        tagElement.textContent = tag;
        tagsContainer.appendChild(tagElement);
    });
    button.appendChild(tagsContainer);

    playlistContainer.appendChild(button);

    const playlistEdit = document.createElement('div');
    playlistEdit.classList.add('playlist-edit');
    playlistEdit.style.display = 'none';
    const editButton = document.createElement('button');
    editButton.classList.add('playlist');
    editButton.textContent = 'Edit';
    playlistEdit.appendChild(editButton);
    playlistContainer.appendChild(playlistEdit);

    return playlistContainer;
}

function redirectToEdit(playlistId) {
    window.location.href = "/edit-playlist/" + playlistId;
}

function redirectToViewPlaylist(playlistId) {
    window.location.href = "/playlist/" + playlistId;
}




// // Gets playlists for a userID
// function getPlaylists(userID) {
//     return new Promise((resolve, reject) => {
//         const xhr = new XMLHttpRequest();
//         xhr.open('GET', `/api/getPlaylists?userID=${userID}`, true);
//         xhr.onload = function() {
//             if (xhr.status >= 200 && xhr.status < 300) {
//                 const response = JSON.parse(xhr.responseText);
//                 console.log("Getting response from getPlaylists...")
//                 console.log(response);
//                 resolve(response.playlists); 
//             } else {
//                 reject(xhr.statusText);
//             }
//         };
//         xhr.onerror = function() {
//             reject(xhr.statusText);
//         };
//         xhr.send();
//     });
// }


// // Usage example:
// const userID = 'yourUserID';
// getPlaylists(userID)
//     .then(playlists => {
//         // Assuming playlists is an array of playlist objects
//         // Render the playlists on the page
//         playlists.forEach(playlist => {
//             renderPlaylist(playlist);
//         });
//     })
//     .catch(error => {
//         console.error('Error retrieving playlists:', error);
//     });

// // Function to render a playlist on the page
// function renderPlaylist(playlist) {
//     // Assuming there's a container element where playlists will be appended
//     const container = document.querySelector('.pure-g');

//     // Create a div element to hold the playlist
//     const playlistDiv = document.createElement('div');
//     playlistDiv.classList.add('pure-u-1', 'pure-u-md-1-3', 'pure-u-lg-1-5', 'playlist-container');

//     // Populate the playlistDiv with playlist information using template literal
//     playlistDiv.innerHTML = `
//         <button class="playlist">
//             <div class="playlist-icon">
//                 <img src="${playlist.image}" alt="Playlist Image">
//             </div>
//             <div class="playlist-name">${playlist.name}</div>
//             <div class="playlist-rating">${playlist.rating}</div>
//             <div class="pure-g playlist-tags">
//                 ${playlist.tags.map(tag => `<div class="tag pure-u-1-3">${tag}</div>`).join('')}
//             </div>
//         </button>
//         <div class="playlist-edit" style="display: none;">
//             <button class="playlist">Edit</button>
//         </div>
//     `;

//     // Append the playlistDiv to the container
//     container.appendChild(playlistDiv);
// }




        /*
        // Gets all search results JSON from server for playlist results when page loads
        function onPageLoad() {
            fetch('/getSearchResults')  // can change to whatever the endpoint is
                .then(response => {
                    if (!response.ok) {
                        throw new Error('No search results response from server');
                    }
                    search_response = response.text();  // Stores entire search results for current query. Rudamentary.
                    return search_response;
                })
                .then(data => { 
                    document.getElementById('playlist').innerHTML = data['playlist'];
                    document.getElementById('playlist').style.display = "block";
                    activeTab = 'playlist';
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        }
        // Alters display when user clicks a new tab
        function changeTabs(newTab){
            document.getElementById(current_tab).style.display = "none";
            current_tab = newTab;
            document.getElementById('playlist').innerHTML = data[newTab];
            document.getElementById(newTab).style.display = "block";
        }
        window.onload = onPageLoad;
        */