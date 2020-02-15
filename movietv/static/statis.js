function buildHotRequest() {
    let url = 'hottest?';
    let sl = document.querySelector('#days');
    let input = document.querySelector('#rdays');

    url += 'days=' + sl.value;

    if (input.value.length != 0 && input.value != '0') {
        url += '&rdays=' + input.value;
    }

    return url;
}
function buildCelebRequest() {
    let url = 'celebrity?';
    let input = document.querySelector('#names');

    url += 'names=' + input.value.replace(/，/g, ',');
    return url;
}
document.addEventListener('DOMContentLoaded', function(){
    let bton = document.querySelector('#hotsubmit');

    bton.addEventListener('click', e => {
        fetch(buildHotRequest()).
            then((response) => response.text()).
            then((html) => {
                let div = document.querySelector('#hotimg');

                div.innerHTML = html;
            });
    });

    bton = document.querySelector('#celebsubmit');
    bton.addEventListener('click', e => {
        fetch(buildCelebRequest()).
            then((response) => response.text()).
            then((html) => {
                let div = document.querySelector('#celebimg')

                div.innerHTML = html;
            });
    });
});
