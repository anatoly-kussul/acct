/**
 * Created by anatoly on 10.12.16.
 */
function set_timer(timer) {
    var cur_seconds, hours, minutes, seconds;
    var start_seconds = timer.getAttribute('data-start');
    setInterval(function () {
        cur_seconds = start_seconds;
        hours = parseInt(cur_seconds / 3600);
        cur_seconds = cur_seconds % 3600;
        minutes = parseInt(cur_seconds / 60);
        seconds = parseInt(cur_seconds % 60);
        if (hours < 10){
            hours = '0' + hours;
        }
        if (minutes < 10){
            minutes = '0' + minutes;
        }
        if (seconds < 10){
            seconds = '0' + seconds;
        }
        timer.innerHTML = hours + ':' + minutes + ':' + seconds;
        start_seconds++;
    }, 1000);
}
function init_timers() {
    var timers = document.getElementsByClassName('timer');
    var i;
    for (i=0; i<timers.length; i=i+1){
        set_timer(timers[i]);
    }
}
$(document).ready(init_timers);
