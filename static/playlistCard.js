// function createPlaylistCard(playlist, user_id, redirect_to_edit=true) {
//     console.log("Creating playlist card")
//     const playlistContainer = document.createElement('div');
//     playlistContainer.classList.add('pure-u-1', 'pure-u-md-1-3', 'pure-u-lg-1-5', 'playlist-container');

//     const button = document.createElement('button');
//     button.classList.add('playlist');
//     if (redirect_to_edit && (playlist.user_id === user_id)){
//         button.onclick = function() {  // redirect to edit playlist page
//             redirectToEdit(playlist.playlistID);
//         }; 
//     }
//     else{
//         button.onclick = function() {
//             redirectToViewPlaylist(playlist.playlistID);
//         };
//     }

//     // const playlistIcon = document.createElement('div');
//     // playlistIcon.classList.add('playlist-icon');
//     // const image = document.createElement('img');
//     // image.src = playlist.image;
//     // image.alt = 'Playlist Image';
//     // playlistIcon.appendChild(image);
//     // button.appendChild(playlistIcon);

//     const playlistName = document.createElement('div');
//     playlistName.classList.add('playlist-name');
//     playlistName.textContent = playlist.name;
//     button.appendChild(playlistName);

//     const playlistRating = document.createElement('div');
//     playlistRating.classList.add('playlist-rating');
//     playlistRating.textContent = playlist.rating;
//     button.appendChild(playlistRating);

//     const tagsContainer = document.createElement('div');
//     tagsContainer.classList.add('pure-g', 'playlist-tags');
//     playlist.tags.forEach(tag => {
//         const tagElement = document.createElement('div');
//         tagElement.classList.add('tag', 'pure-u-1-3');
//         tagElement.textContent = tag;
//         tagsContainer.appendChild(tagElement);
//     });
//     button.appendChild(tagsContainer);

//     playlistContainer.appendChild(button);

//     const playlistEdit = document.createElement('div');
//     playlistEdit.classList.add('playlist-edit');
//     playlistEdit.style.display = 'none';
//     const editButton = document.createElement('button');
//     editButton.classList.add('playlist');
//     editButton.textContent = 'Edit';
//     playlistEdit.appendChild(editButton);
//     playlistContainer.appendChild(playlistEdit);

//     return playlistContainer;
// }

function createPlaylistCard(playlist, user_id, redirect_to_edit=true) {
    console.log("Creating playlist card");
    const playlistContainer = document.createElement('div');
    playlistContainer.classList.add('pure-u-1', 'pure-u-md-1-3', 'pure-u-lg-1-5', 'playlist-container');

    const button = document.createElement('button');
    button.classList.add('playlist');
    button.onclick = function() {
        if (redirect_to_edit && playlist.user_id === user_id) {
            redirectToEdit(playlist.playlistID);
        } else {
            redirectToViewPlaylist(playlist.playlistID);
        }
    };

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

    return playlistContainer;
}



function redirectToEdit(playlistId) {
    window.location.href = "/edit-playlist/" + playlistId;
}

function redirectToViewPlaylist(playlistId) {
    window.location.href = "/playlist/" + playlistId;
}



function makeDeleteSongCard(song){
    console.log("Called makeDeleteSongCard with ", song);
    // Creating elements dynamically
    var songDiv = document.createElement("div");
    songDiv.className = "pure-g song";

    var songIconDiv = document.createElement("div");
    songIconDiv.className = "pure-u-1-5 song-icon";
    var songIconImg = document.createElement("img");
    songIconImg.src = song.songImage;
    songIconImg.alt = "Song Icon";
    songIconDiv.appendChild(songIconImg);

    var songTitleDiv = document.createElement("div");
    songTitleDiv.className = "pure-u-3-5 song-title";
    songTitleDiv.textContent = song.songName;

    var deleteButton = document.createElement("button");
    deleteButton.className = "add-song";
    deleteButton.setAttribute("onclick", "deleteSong('" + song.songID + "', '" + song.songName + "', '" + song.songImage + "')");
    var deleteButtonText = document.createElement("h1");
    deleteButtonText.textContent = "-";
    deleteButton.appendChild(deleteButtonText);

    deleteButton.addEventListener("click", function(event) {
        event.stopPropagation(); // Prevent parent event triggering
    });

    // Appending elements to songDiv
    songDiv.appendChild(songIconDiv);
    songDiv.appendChild(songTitleDiv);
    songDiv.appendChild(deleteButton);
    console.log("Made songDiv", songDiv);
    return songDiv;
}