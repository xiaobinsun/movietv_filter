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
function buildTimeRange(addAm, bid, eid) {
    let str = '';
    let ts = document.querySelector(bid);
    let te = document.querySelector(eid);
    if (ts.value.length != 0 && ts.value != '0')
        str += ts.value;
    str += ',';
    if (te.value.length != 0)
        str += te.value;
    if (str == ',') {
        str = '';
    } else {
        if (addAm)
            str = '&timerange=' + str;
        else
            str = 'timerange=' + str;
    }
    return str;
}

function buildType(addAm) {
    str = '';
    let tp = document.querySelector('#type');

    if (tp.value == '全部类型')
        return str;
    if (addAm) {
        str += '&type=' + tp.value;
    } else {
        str += 'type=' + tp.value;
    }

    return str;
}

function buildRbarRequest() {
    let url = 'regionbar/?';

    url += buildTimeRange(url[url.length-1] != '?', '#begin', '#end');
    url += buildType(url[url.length-1] != '?');

    return url;
}
function buildTypebarRequest() {
    let url = 'typebar/?';

    url += buildTimeRange(url[url.length-1] != '?', '#tbegin', '#tend');
    if (url[url.length-1] == '?')
        url = 'typebar/'

    return url
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

    bton = document.querySelector('#rbarsubmit');
    bton.addEventListener('click', e => {
        fetch(buildRbarRequest()).
            then((response) => response.text()).
            then((html) => {
                let div = document.querySelector('#rbarimg');

                div.innerHTML = html;
            });
    });

    bton = document.querySelector('#typebarsubmit');
    bton.addEventListener('click', e => {
        fetch(buildTypebarRequest()).
            then((response) => response.text()).
            then((html) => {
                let div = document.querySelector('#typebarimg');

                div.innerHTML = html;
            });
    });
});
