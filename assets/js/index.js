document.addEventListener('DOMContentLoaded', () => {
    loadOnglerieList();
    loadRegardList()

    document.querySelector('#openIcon').addEventListener('click', openNav);
    document.querySelector('#closeIcon').addEventListener('click', closeNav);
})

function openNav() {
    document.querySelector('#openIcon').style.display = 'none';
    document.querySelector('#closeIcon').style.display = 'block';
    document.querySelector('nav').style.display = 'flex';
}

function closeNav() {
    document.querySelector('#closeIcon').style.display = 'none';
    document.querySelector('nav').style.display = 'none';
    document.querySelector('#openIcon').style.display = 'block';
}

function loadOnglerieList() {
    fetch('./assets/data/onglerie.json')
        .then(response => response.json())
        .then(datas => {
            datas.forEach(data => {
                const tr = document.createElement('tr');

                tr.innerHTML = `
                    <td>${data.name}</td>
                    <td>${data.price}</td>
                `

                document.querySelector("#onglerie-list").append(tr)
            });
        });
};

function loadRegardList() {
    fetch('./assets/data/regard.json')
        .then(response => response.json())
        .then(datas => {

            datas.forEach(data => {
                const tr = document.createElement('tr');

                tr.innerHTML = `
                    <td>${data.name}</td>
                    <td>${data.price}</td>
                `

                document.querySelector("#regard-list").append(tr)
            });
        });
};

function loadViewer(number) {
    // Load a number of images in gallery
    const images_number = number;

    for (i = 0; i < images_number; i + 1) {
        // Create an image
        const img = document.createElement("img");

        img.src = `./assets/images/gallery/${i}.webp`;
        img.alt = "Photo réalisation Beauty Star";

        const div = document.createElement('div');

        // Add image in viewer
        document.querySelector("#realisations-viewer").append(img);

        i++;
    }
}

