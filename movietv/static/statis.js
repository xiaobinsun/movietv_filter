function buildHotRequest() {
    let url = '?';
    let sl = document.querySelector('#days');
    let input = document.querySelector('#rdays');

    url += 'days=' + sl.value;

    if (input.value.length != 0 && input.value != '0') {
        url += '&rdays=' + input.value;
    }

    return url;
}
document.addEventListener('DOMContentLoaded', function(){
    let bton = document.querySelector('#hotsubmit');

    bton.addEventListener('click', e => {
        fetch(buildHotRequest()).
            then((response) => response.text()).
            then((html) => {
                let div = document.querySelector('#imgdiv');

                div.innerHTML = html;
            });
    });
});
