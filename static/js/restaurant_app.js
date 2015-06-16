(function(){
    var app = angular.module('restaurants', []);

    app.controller("PanelController", function($scope, ReviewsService, MapService){
        console.log("PanelController on")
        $scope.tab = 1;
        $scope.add_cancel = "Add a Review";
        $scope.reviewOn = 0;
        $scope.review = {};

        $scope.selectTab = function(setTab) {
            $scope.tab = setTab;
            console.log("We set tab: ", $scope.tab)
        };

        $scope.isSelected = function(checkTab) {
            return $scope.tab === checkTab;
        };

        $scope.showReviewToggle = function() {
            if ($scope.reviewOn === 1) {
                $scope.reviewOn = 0;
                $scope.add_cancel = "Add a Review"
            }else {
                $scope.reviewOn = 1;
                $scope.add_cancel = "Cancel"
            };
        };

        $scope.showReviewOn = function() {
            return $scope.reviewOn === 1;
        };

        $scope.getReviews = function(restaurant_id) {
            console.log("Inside getReviews")
            ReviewsService.getReviews(restaurant_id).then(function(dataResponse){
                $scope.reviews = dataResponse.data.ReviewsList;
            });
        };

        $scope.addNewReview = function(restaurant_id) {
            console.log("The review object:", $scope.review)
            ReviewsService.addReview(restaurant_id, $scope.review).then(function(dataResponse){
                console.log(dataResponse)
            });
            $scope.getReviews(restaurant_id);
        };

        $scope.getMap = function(address, rid){
            //$scope.map = new google.maps.Map(document.getElementById(rid),{zoom:15, mapTypeId:google.maps.MapTypeId.ROADMAP});

            MapService.initialize(address, rid);
            //MapService.update_maps();
        };


    });


    app.service("ReviewsService", function($http){
        console.log("ReviewsService on")
        //this.review = {};

        this.getReviews = function(restaurant_id) {
            restaurant_url = '/restaurants/' + restaurant_id + '/reviews/JSON';
            return $http({
                method  : 'GET',
                url     : restaurant_url,
                headers : {'Content-Type': 'application/json'},
            });
        }

        this.addReview = function(restaurant_id, review_obj) {
            restaurant_url = '/restaurants/' + restaurant_id + '/addnewreview';
            //console.log(review);
            return $http({
                method  : 'POST',
                url     : restaurant_url,
                data    : review_obj,
                headers : {'Content-Type': 'application/json'},
            });
        };
    });



    app.service("MapService", function(){
        var mymap = this;
        mymap.map;
        mymap.prop;
        mymap.city = "";
        mymap.mapcollection = []
        console.log("MapService on");
        mymap.initialize = function(address, rid){
            var exists = 0
            for (add in mymap.mapcollection){
                if (mymap.mapcollection.length > 0 && mymap.mapcollection[add].city == address){
                    exists = 1;
                }
            };
            console.log("Exists: ", exists)
            if (exists == 0){
                mymap.city = address;
                mymap.prop = {
                    zoom: 15,
                    mapTypeId:google.maps.MapTypeId.ROADMAP
                };
                mymap.map = new google.maps.Map(document.getElementById(rid), mymap.prop);
                console.log("The city is: ", mymap.city)
                console.log(document.getElementById(rid))
                mymap.pinPoster();
                mymap.mapcollection.push(mymap.map);

                //mymap.map.setZoom(mymap.map.getZoom() - 1);
                //mymap.map.setZoom(mymap.map.getZoom() + 1);
                //mymap.map.setCenter(mymap.map.getCenter())
            };

        };


        mymap.placeMarkerOnMap = function(placeData) {
            lat = placeData.geometry.location.lat();
            lon = placeData.geometry.location.lng();
            name = placeData.formatted_address;
            bounds = new google.maps.LatLngBounds(new google.maps.LatLng(lat, lon));

            marker = new google.maps.Marker({
                map: mymap.map,
                position: placeData.geometry.location,
                title: name,
                //animation:google.maps.Animation.BOUNCE
            });

            console.log("Placing marker")
            infoWindow = new google.maps.InfoWindow({
                content: name,
                position: placeData.geometry.location,
            });

            google.maps.event.addListenerOnce(mymap.map, "idle", function(){
                    google.maps.event.trigger(mymap.map, "resize");
                    mymap.map.setCenter(marker.getPosition())
                    //mymap.map.panTo(marker.getPosition())
                //mymap.map.setZoom(mymap.map.getZoom() - 1);
                //mymap.map.setZoom(mymap.map.getZoom() + 1);
            });

            //bounds.extend(new google.maps.LatLng(lat, lon));
            console.log("The bounds: ", bounds);

            console.log("Lat, lon", lat, lon);

            mymap.map.fitBounds(bounds);
            mymap.map.setCenter(bounds.getCenter());
            console.log("map Center is: ", mymap.map.center);
            mymap.map.setZoom(15);

        };

        mymap.callback = function(results, status) {
            if (status == google.maps.places.PlacesServiceStatus.OK) {
                console.log("going to place marker on map with result: ", results[0]);
                mymap.placeMarkerOnMap(results[0]);
            };
        };

        mymap.pinPoster = function() {
            console.log("City is: ", mymap.city)
            mymap.service = new google.maps.places.PlacesService(mymap.map);
            mymap.request = {query: mymap.city};
            mymap.service.textSearch(mymap.request, mymap.callback);
        };

        mymap.update_maps = function() {
            for (var map in mymap.collection){
                    google.maps.event.addListenerOnce(mymap.collection[map], 'idle', function(){

                        google.maps.event.trigger(mymap.collection[map],'resize');
                        mymap.collection[map].setCenter(location);
                    });

            };
        };
    });



})();
