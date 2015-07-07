(function(){
    var app = angular.module('restaurants', ['ui.bootstrap']);

    app.config(['$interpolateProvider', function($interpolateProvider){
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }])

    /* VoteController -
    */

    app.controller("VoteController", function($scope, VoteService){
        $scope.likes = 0;
        $scope.dislikes = 0;
        $scope.item_id = -1;


        /* getVotes */
        $scope.getVote = function() {
            console.log("Inside getVotes, and the item_id is: ", $scope.item_id)
            VoteService.getMenuItemVote($scope.item_id).then(function(dataResponse){
                $scope.likes = dataResponse.data.Item.likes;
                $scope.dislikes = dataResponse.data.Item.dislikes;
            });
        };

        $scope.postVote = function(vote) {
            console.log("inside postvote")
            VoteService.postMenuItemVote($scope.item_id, vote).then(function(dataResponse){
                console.log("We posted!")
                $scope.likes = dataResponse.data.Item.likes;
                $scope.dislikes = dataResponse.data.Item.dislikes;      
            })
        };

        $scope.initVote = function(item_id) {
            if ($scope.item_id == -1) {
                $scope.item_id = item_id
                $scope.getVote()
            };
            return true;

        };


    });

    /* PanelController - 
        Controller for the panel for each restaurant selection, 
        user can select between the description of the restaurant (default),
                                or the reviews (and add reviews), 
                                or view the map to the location. 
    */
    app.controller("PanelController", function($scope, ReviewsService, MapService, ImageService){
        console.log("PanelController on")
        $scope.tab = 1;
        $scope.add_cancel = "Add a Review";
        $scope.reviewOn = 0;
        $scope.review = {};
        $scope.myInterval = 5000;
        $scope.slides = {};

        /* selectTab - 
            sets the tab that the user clicked on 
            (setTab = 1 for description, = 2 for review, = 3 for map)
        */
        $scope.selectTab = function(setTab) {
            $scope.tab = setTab;
            console.log("We set tab: ", $scope.tab)
        };


        /* isSelected - 
            return true/false if a tab was selected (tab number passed as checkTab)
        */
        $scope.isSelected = function(checkTab) {
            return $scope.tab === checkTab;
        };


        /* showReviewToggle -
            toggle the reviews tab, if the correct tab is selected
        */
        $scope.showReviewToggle = function() {
            if ($scope.reviewOn === 1) {
                $scope.reviewOn = 0;
                $scope.add_cancel = "Add a Review"
            }else {
                $scope.reviewOn = 1;
                $scope.add_cancel = "Cancel"
            };
        };


        /* showReviewOn - 
            return true if review tab is selected
        */
        $scope.showReviewOn = function() {
            return $scope.reviewOn === 1;
        };


        /* getReviews - 
            make the API call to get the reviews as JSON object
        */
        $scope.getReviews = function(restaurant_id) {
            console.log("Inside getReviews")
            ReviewsService.getReviews(restaurant_id).then(function(dataResponse){
                $scope.reviews = dataResponse.data.ReviewsList;
            });
        };


        /* addNewReview -
            add a new review to the database
        */
        $scope.addNewReview = function(restaurant_id) {
            console.log("The review object:", $scope.review)
            ReviewsService.addReview(restaurant_id, $scope.review).then(function(dataResponse){
                console.log(dataResponse)
            });
            $scope.getReviews(restaurant_id);
        };


        /* getMap - 
            initialize the map to the location of the restaurant. 
        */
        $scope.getMap = function(address, rid){
            //$scope.map = new google.maps.Map(document.getElementById(rid),{zoom:15, mapTypeId:google.maps.MapTypeId.ROADMAP});
            //TODO : right now, we are passing the restaurant name and address
            //       in the future we want to check the restaurant first, if that DOESN't work, then address
            console.log(address)
            MapService.initialize(address, rid);
            MapService.update_maps();
        };

        $scope.addSlides = function(restaurant_id) {
            console.log("in addslides!", restaurant_id)
            var newWidth = 600 + $scope.slides.length + 1;
            ImageService.getRestaurantImages(restaurant_id).then(function(dataResponse){
                $scope.slides = dataResponse.data.RestaurantImagesList
            });
            console.log("The slides obtained are: ", $scope.slides)
        };

    });


    /* ReviewService - 
        Service to get the reviews and send new reviews to the database
    */
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
            console.log("Sending HTTP req to ", restaurant_url);
            console.log("Review Obj, ", review_obj)
            return $http({
                method  : 'POST',
                url     : restaurant_url,
                data    : review_obj,
                headers : {'Content-Type': 'application/json'},
            });
        };
    });


    /* MapService - 
        Get the google map and place marker on the address of the restaurant
    */
    app.service("MapService", function(){
        var mymap = this;
        mymap.map;
        mymap.prop;
        mymap.city = "";
        mymap.mapcollection = []    // to contain all maps for all restaurants
        console.log("MapService on");
        

        /* initialize - 
            get the map from google maps service
            place the pin on the map
            add map to a collection of maps (so we can repeat for all restaurants)
        */
        mymap.initialize = function(address, rid){
            var exists = 0
            // if map already exists, don't create a new map
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

    
    app.service("ImageService", function($http){
        console.log("ImageService on")
        //this.review = {};


        this.getRestaurantImages = function(restaurant_id) {
            restaurant_img_url = '/restaurants/images/' + restaurant_id + '/JSON';
            return $http({
                method  : 'GET',
                url     : restaurant_img_url,
                headers : {'Content-Type': 'application/json'},
            });
        }


        this.addReview = function(restaurant_id, review_obj) {
            restaurant_url = '/restaurants/' + restaurant_id + '/addnewreview';
            console.log("Sending HTTP req to ", restaurant_url);
            return $http({
                method  : 'POST',
                url     : restaurant_url,
                data    : review_obj,
                headers : {'Content-Type': 'application/json'},
            });
        };
    });


    app.service("VoteService", function($http){
        console.log("VoteService on")
        //this.review = {};

        this.getMenuItemVote = function(item_id) {
            menu_votes_url = '/restaurants/vote/' + item_id + '/'+ 0;
            console.log("The url is: ", menu_votes_url)
             return $http({
                 method  : 'GET',
                 url     : menu_votes_url,
                 headers : {'Content-Type': 'application/json'},
            });
        }


        this.postMenuItemVote = function(item_id, vote) {
            menu_votes_url = '/restaurants/vote/' + item_id + '/' + vote;
            console.log("Sending HTTP req to ", menu_votes_url);
            return $http({
                method  : 'POST',
                url     : menu_votes_url,
                data    : vote,
                headers : {'Content-Type': 'application/json'},
            });
        };
    });

})();
