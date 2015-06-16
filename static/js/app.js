(function(){                                        // lets wrap our application in a closure, good habit to get into
    var app = angular.module('restaurant', []);
    app.controller('RestaurantController', function(){   // Controllers are where we defined out apps behavior by defining functions and values
                                                    // Its important that the controller is named as such - capital/camel case.
                                                    // Also it is important to have the word 'controller' in the name
                                                    // the generic function() will describe what happens when our controller is called                         // we need to set the gem as a property of our controller, called "product"
    });

    app.controller("PanelController", function(){
        this.tab = 1;
        this.reviewOn = 0;

        this.selectTab = function(setTab) {
            this.tab = setTab;
            console.log("We set tab: ", this.tab)
        };
        this.isSelected = function(checkTab){
            console.log("We have confirmed the selection: ", this.tab)
            return this.tab === checkTab;

        };
        this.showReviewToggle = function() {
            if (this.reviewOn == 1){
                this.reviewOn = 0;
                console.log("Review will be hidden")

            }else{
                this.reviewOn = 1;
                console.log("Review will be displayed")

            }
        };
        this.showReviewOn = function(){
            return this.reviewOn == 1
        };

    });

    app.controller('customersCtrl', function($http) {
    console.log("In customers control");
    this.getReviews = function(rest_id){
        this.url = "/restaurants/" +rest_id+"/reviews/JSON";
        $http.get(this.url)
        .success(function(response) {this.names = response.ReviewsList;});
        console.log(this.names)
    };
    });

    app.controller("ReviewController", function($scope, $http){
        $scope.collection = {};
        $scope.review={};
        $scope.test = 'Testing Testing';
        console.log("Review Controller on");
        this.getReviews = function(rest_id){
            console.log("inside get reviews")
            $scope.siz = 0;
            //url = "/restaurants/" + rest_id + "/reviews/JSON";
            url = "http://www.w3schools.com/angular/customers.php";
            $http.get(url).success(function(response){
                //this.collection = data.ReviewsList;
                $scope.names = response.records
                //$scope.collection = data;
                //console.log($scope.collection);
                //$scope.siz = $scope.collection.length;
                //console.log("The size of the collection post checking:", $scope.siz)
            /*for (rev in this.collection){
                console.log("In for")
                console.log("Each review is: ", this.collection[rev].reviewer_name);
            };*/
            });
        };


        this.addReview = function(rest_id){
            //product.reviews.push(this.review);
            //this.review={};
            console.log("The author is: ", $scope.review)
            $http({
                url     : "/restaurants/" + rest_id + "/addnewreview",
                method  : "POST",
                data    : this.review,
                headers : {'Content-Type': 'application/json'}

            }).success(function(){
                console.log('status', status);
                console.log('data', status);
                console.log('headers', status);
            });


        };

    });
    /*
    app.config(function($interpolateProvider){
        $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
    });
    */

    app.controller("MapController", function(){
        var mymap = this;
        mymap.map;
        mymap.prop;
        mymap.city = "";
        mymap.mapcollection = []
        console.log("Map Controller on");
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

                mymap.pinPoster();
                mymap.mapcollection.push(mymap.map)

                //mymap.map.setZoom(mymap.map.getZoom() - 1);
                //mymap.map.setZoom(mymap.map.getZoom() + 1);
                //mymap.map.setCenter(mymap.map.getCenter())
            };

        };


        mymap.createMapMarker = function(placeData) {
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
            })

            google.maps.event.addListenerOnce(mymap.map, "idle", function(){
                    google.maps.event.trigger(mymap.map, "resize");
                    mymap.map.setCenter(marker.getPosition())
                    //mymap.map.panTo(marker.getPosition())
                //mymap.map.setZoom(mymap.map.getZoom() - 1);
                //mymap.map.setZoom(mymap.map.getZoom() + 1);
            });

            //bounds.extend(new google.maps.LatLng(lat, lon));
            console.log("The bounds: ", bounds)

            console.log("Lat, lon", lat, lon)

            mymap.map.fitBounds(bounds);
            mymap.map.setCenter(bounds.getCenter());
            console.log("map Center is: ", mymap.map.center)
            mymap.map.setZoom(15);



        };

        mymap.callback = function(results, status) {
            if (status == google.maps.places.PlacesServiceStatus.OK) {
                mymap.createMapMarker(results[0]);
            }
        };

        mymap.pinPoster = function() {
            console.log("City is: ", mymap.city)
            mymap.service = new google.maps.places.PlacesService(mymap.map);
            mymap.request = {query: mymap.city};
            mymap.service.textSearch(mymap.request, mymap.callback);
        };

        for (var map in mymap.collection){
                google.maps.event.addListenerOnce(mymap.collection[map], 'idle', function(){

                    google.maps.event.trigger(mymap.collection[map],'resize');
                    mymap.collection[map].setCenter(location);
                });

        };

        /*
        google.maps.event.addDomListener(window, 'resize', function(){
            for (map in mymap.collection){
                mymap.collection[map].setCenter(homeLatlng);
            }

        });
        */
        //window.mapBounds = new google.maps.LatLngBounds();

        //window.addEventListener('load', initialize);
        //window.addEventListener('resize', function(e){
        //    console.log("Resize seen.")
        //    mymap.map.fitBounds(mapBounds);
        //});

        //mymap.pinPoster();
    });

    app.directive('existingReviews', function(){
        return {
            restrict: 'E',
            templateUrl: 'existing-reviews.html',
        }
    });


})();
