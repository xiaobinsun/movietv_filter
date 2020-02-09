function buildForm(addAm) {
    let str = '';
    let fm = document.querySelector('#form .selected').querySelector('span').innerHTML.trim();
    if (!fm.includes('全部')) {
        if (addAm)
            str += '&';
        str += 'form=';
        str += fm;
    }
    return str;
}
function buildRegion(addAm) {
    let str = '';
    let fm = document.querySelector('#region .selected').querySelector('span').innerHTML.trim();
    if (!fm.includes('全部')) {
        if (addAm)
            str += '&';
        str += 'region=';
        str += fm;
    }
    return str;
}
function buildType(addAm) {
    let str = '';
    let ul = document.querySelector('#type');
    for (let elm of ul.querySelectorAll('li.selected')) {
        let s = elm.querySelector('span').innerHTML.trim();
        if (s.includes('全部'))
            break;
        str += s;
        str += ',';
    }
    if (str.length > 0) {
        str = str.substring(0, str.length-1);
        if (addAm)
            str = '&type=' + str;
        else
            str = 'type=' + str;
    }
    return str;
}
function buildTimeRange(addAm) {
    let str = '';
    let ts = document.querySelector('#begin');
    let te = document.querySelector('#end');
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
function buildScoreRange(addAm) {
    let str = '';
    let ss = document.querySelector('#sbegin');
    let se = document.querySelector('#send');
    if (ss.value.length != 0 && ss.value != '0')
        str += ss.value;
    str += ',';
    if (se.value.length != 0)
        str += se.value;
    if (str == ',') {
        str = '';
    } else {
        if (addAm)
            str = '&scorerange=' + str;
        else
            str = 'scorerange=' + str;
    }
    return str;
}
function buildVotesRange(addAm) {
    let str = '';
    let vs = document.querySelector('#vbegin');
    let ve = document.querySelector('#vend');
    if (vs.value.length != 0 && vs.value != '0')
        str += vs.value;
    str += ',';
    if (ve.value.length != 0)
        str += ve.value;
    if (str == ',') {
        str = '';
    } else {
        if (addAm)
            str = '&votesrange=' + str;
        else
            str = 'votesrange=' + str;
    }
    return str;
}
function buildPage(addAm) {
    let str = '';
    let sl = document.querySelector('#step-links');

    if (addAm)
        str += '&page=' + sl.curpage;
    else
        str += 'page=' + sl.curpage;

    return str;
}
function buildFetchArgs() {
    let url = 'filter?';
    url += buildForm(url[url.length-1] != '?');
    url += buildType(url[url.length-1] != '?');
    url += buildRegion(url[url.length-1] != '?');
    url += buildTimeRange(url[url.length-1] != '?');
    url += buildScoreRange(url[url.length-1] != '?');
    url += buildVotesRange(url[url.length-1] != '?');
    url += buildPage(url[url.length-1] != '?');
    return url;
}
function fireFetch() {
    fetch(buildFetchArgs())
        .then((response) => response.text())
        .then((html) => {
            let doc = new DOMParser().parseFromString(html, 'text/html');
            let tbody = doc.querySelector('tbody');
            document.querySelector('#rbody').innerHTML = tbody.innerHTML;

            let pagi = doc.querySelector('#step-links');
            document.querySelector('#step-links').innerHTML = pagi.innerHTML;

            let alist = document.querySelectorAll('#step-links > button');
            alist.forEach(item => item.addEventListener('click', pageSelect));

            let sl = document.querySelector('#step-links');
            if (sl.curpage == undefined) {
                sl.curpage = 1;
            }

            sl.querySelectorAll('button').forEach(elm => {
                if (elm.id == '#') {
                    elm.classList.add('disabled');
                }
                if (elm.id == sl.curpage) {
                    elm.classList.add('curpage');
                }
            });
        });
}
function pageSelect(e) {
    let sl = document.querySelector('#step-links');

    if (sl.curpage != this.id) {
        sl.curpage = this.id;
        fireFetch();
    }
}
function liClick(e) {
    let ul = this.parentNode;
    let tag = this.querySelector('span').innerHTML;
    if (ul.classList.contains('singleops')) {
        for (let elm of ul.children) {
            elm.classList.remove('selected');
        }
        this.classList.add('selected');
    } else if (ul.classList.contains('multipleops')) {
        if (tag.includes('全部')) {
            for (let elm of ul.children) {
                elm.classList.remove('selected');
            }
            this.classList.add('selected');
        } else {
            ul.firstElementChild.classList.remove('selected');
            if (this.classList.contains('selected'))
                this.classList.remove('selected');
            else
                this.classList.add('selected');
            if (ul.querySelectorAll('li.selected').length == 0)
                ul.firstElementChild.classList.add('selected');
        }
    }
    fireFetch();
}
document.addEventListener('DOMContentLoaded', function(){
    let elist = document.querySelectorAll("body > ul > li");
    elist.forEach(item => item.addEventListener('click', liClick));

    let bton = document.querySelector('#submit');
    bton.addEventListener('click', fireFetch);
    fireFetch();
});
