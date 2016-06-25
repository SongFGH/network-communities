function initMap() {
    console.log("ssss");
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 4,
        center: {lat: 38.563265, lng: -95.186107},
        mapTypeControl: false,
        /*styles: [{"featureType":"landscape","stylers":[{"saturation":-100},{"lightness":65},{"visibility":"on"}]},{"featureType":"poi","stylers":[{"saturation":-100},{"lightness":51},{"visibility":"simplified"}]},{"featureType":"road.highway","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"road.arterial","stylers":[{"saturation":-100},{"lightness":30},{"visibility":"on"}]},{"featureType":"road.local","stylers":[{"saturation":-100},{"lightness":40},{"visibility":"on"}]},{"featureType":"transit","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"administrative.province","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":-25},{"saturation":-100}]},{"featureType":"water","elementType":"geometry","stylers":[{"hue":"#ffff00"},{"lightness":-25},{"saturation":-97}]}]*/ //original style
        styles: [{"featureType":"administrative.locality","elementType":"geometry","stylers":[{"visibility":"simplified"}]},{"featureType":"administrative.locality","elementType":"labels","stylers":[{"visibility":"simplified"}]}]
    });

    var pinColors = ["382DD4", "FE7569"];
    var pinShadow = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_shadow",
        new google.maps.Size(40, 37),
        new google.maps.Point(0, 0),
        new google.maps.Point(12, 35));

    var geocoder = new google.maps.Geocoder();
    var bounds = new google.maps.LatLngBounds();
    var url = "static/img/airport.png";

    for (var i=0; i < airports.length; i++) {

        var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + pinColors[i],
            new google.maps.Size(21, 34),
            new google.maps.Point(0,0),
            new google.maps.Point(10, 34));

        geocoder.geocode({'address': airports[i]['code']}, function (results, status) {
            CODE = results[0].geometry.location;
            bounds.extend(CODE);
            var marker = new google.maps.Marker({
                map: map,
                position: results[0].geometry.location,
                icon: pinImage,
                shadow: pinShadow
            });
        });
    }
    }
