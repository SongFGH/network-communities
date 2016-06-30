
function getHexColor() {
    return Math.floor(Math.random()*16777215).toString(16);
}

function initMap() {

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 5,
        center: {lat: 38.563265, lng: -95.186107},
        // center: {lat: 47.512878, lng: -116.934964},
        mapTypeControl: false,
        /*styles: [{"featureType":"landscape","stylers":[{"saturation":-100},{"lightness":65},{"visibility":"on"}]},{"featureType":"poi","stylers":[{"saturation":-100},{"lightness":51},{"visibility":"simplified"}]},{"featureType":"road.highway","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"road.arterial","stylers":[{"saturation":-100},{"lightness":30},{"visibility":"on"}]},{"featureType":"road.local","stylers":[{"saturation":-100},{"lightness":40},{"visibility":"on"}]},{"featureType":"transit","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"administrative.province","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":-25},{"saturation":-100}]},{"featureType":"water","elementType":"geometry","stylers":[{"hue":"#ffff00"},{"lightness":-25},{"saturation":-97}]}]*/ //original style
        styles: [{"featureType":"administrative.locality","elementType":"geometry","stylers":[{"visibility":"simplified"}]},{"featureType":"administrative.locality","elementType":"labels","stylers":[{"visibility":"simplified"}]}]
    });

    var pinColors = ["7F1416", "41D441", "0079C0", "CDB5E4", "31B59B"];
    // var pinColors = ["7F1416"];
    for (var k=0; k < airports.length; k++) {
        var color = getHexColor();
        pinColors.push(color);
        // pinColors.push("B8B8B8");
    }
    // var pinColors = ["382DD4", "FE7569", "30EF89", "F8FF15", "FF9A15", "FF33FF", "15F0FF", "1583FF", "999999", "CC6666", "996BDE", "000000", "0D8A47"];

    var pinShadow = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_shadow",
        new google.maps.Size(40, 37),
        new google.maps.Point(0, 0),
        new google.maps.Point(12, 35));

    var geocoder = new google.maps.Geocoder();
    var bounds = new google.maps.LatLngBounds();
    var url = "static/img/airport.png";

    for (var i=0; i < airports.length; i++) {

        (function(){
            var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + pinColors[i],
                new google.maps.Size(21, 34),
                new google.maps.Point(0,0),
                new google.maps.Point(10, 34));

            for (var k=0; k < airports[i].length; k++) {

                var marker = new google.maps.Marker({
                    map: map,
                    position: {lat: Number(airports[i][k]['lat']), lng: Number(airports[i][k]['lon'])},
                    icon: pinImage,
                    shadow: pinShadow,
                    title: String(airports[i][k]['code'])
                });
            }
        })();
    }
}
