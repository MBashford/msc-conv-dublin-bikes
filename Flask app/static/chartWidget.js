//define ip address of flask server - placeholder
var host = "http://127.0.0.1:5000/";

var times = ["05.00", "06.00", "07.00","08.00", "09.00", "10.00", "11.00", "12.00", "13.00", "14.00", "15.00", "16.00", "17.00", "18.00", "19.00", "20.00", "21.00", "22.00", "23.00", "24.00"];
var freeStands = [15, 34, 45, 56, 67, 45 , 1, 34, 78, 5, 15, 34, 45, 56, 67, 45 , 1 ,34, 78, 5];
var freeBikes = [75, 56, 45, 34, 23, 45, 89, 56, 12, 85, 75, 56, 45, 34, 23, 45, 89, 56, 12, 85];
var borderColours = ["rgb(64, 204, 219)", "rgb(184, 202, 204)"];
var fillColours = ["rgba(64, 204, 219, 0.8)", "rgba(184, 202, 204, 0.5)"];

// an object for holding the predication data returned from the server for the currently selected stationId
var stationPredictionData = {};

/*
// extend chart type "line" to include a vertical line denoting current hour/day/etc
// source: https://stackoverflow.com/questions/30256695/chart-js-drawing-an-arbitrary-vertical-line
var originalLineController = Chart.controllers.line;
Chart.controllers.line = Chart.controllers.line.extend({
    draw: function () {
        originalLineController.prototype.draw.apply(this, arguments);

        console.log(this);

        var point = this._data[0][this.chart.options.lineAtIndex];
        var scale = this.scale;

        // draw line
        this.chart.ctx.beginPath();
        this.chart.ctx.moveTo(point.x, scale.startPoint + 24);
        this.chart.ctx.strokeStyle = '#ff0000';
        this.chart.ctx.lineTo(point.x, scale.endPoint);
        this.chart.ctx.stroke();

        // write TODAY
        this.chart.ctx.textAlign = 'center';
        this.chart.ctx.fillText("TODAY", point.x, scale.startPoint + 12);
    }
});
*/

function createChart(elemId, labels, dataPoints, dataLabels,  borderColours, fillColours) {
    // creates a chartJS stacked-line-graph with a categorical x-axis in the passed html <canvas id=[elemId]> element
    // elemId: specifies the element Id of the container for the chart
    // labels: the labels for the x-axis categories
    // dataPoints: an array of arrays containing y co-ordinates for each line
    //          ie. [ [ line1: y1, y2, y3...], [ line2: y1, y2, y3, ...] ]
    // dataLabels: an array containing the labels for each line
    // borderColours: an array containing the line/border colour for each line
    // fillColours: an array containing the fill colour beneath each line


    function DataSet(data, label, fill, fillColor, borderColor, lineTension) {
        // formats the passed data as an object w/ instance variables to be passed
        // to the Chart() object constructor
        this.label = label;
        this.fill = fill;
        this.backgroundColor = fillColor;
        this.borderColor = borderColor;
        this.lineTension = lineTension;
        this.pointRadius = 0;

        var arr = new Array();


        Object.keys(data).forEach( function(item) {
            arr.push(data[item])
        })

        this.data = arr;
    }

    // get the chart container from the info.html page
    var ctx = document.getElementById(elemId);

    lines = [];
    for (var i = 0; i < dataPoints.length; i++) {
        var t = new DataSet(dataPoints[i], dataLabels[i], true, fillColours[i], borderColours[i], 0.1);
        lines.push(t);
    }
    console.log(lines);

    new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: lines
            },
            options: {
                scales: {
                    yAxes: [{
                        stacked: true,
                        display: false,
                    }]
                },
                legend : {
                    position: "left"
                },
                lineAtIndex: 2
            }
    });
}

function getChartData(stationId) {
    // request prediction data for the passed station ID for generating graphs

    fetch( host + "get_station_prediction?id=" + stationId, {mode: "cors", method: "GET",})
        .then(response => response.json())
        //.then(body => console.log(body))
        .then(
            function(body) {
                stationPredictionData = body;
                return true;
            })
        .catch(
            function(error) {
                console.log('Request failed', error);
                return false;
        });
}


function populateSelectOptions(dropdownId, chartName) {
    // populates the dropdown selection box corresponding to the passed dropdownId
    // with the values contained in chartName.chartKeys
    var selectionList = document.getElementById(dropdownId);
    options = Object.keys(stationPredictionData[chartName].dataSets);
    for (let i of options) {
        document.getElementById("bikesByHourBtns").innerHTML += '<button type="button" class="btn" onclick=changeHourlyGraph("' + i + '")>' + i + '</button>'
        //selectionList.innerHTML += '<option value="' + i + '" onclick=changeHourlyGraph(' + i + ') >' + i + '</option>';
    }
}


async function chartMain(stationId) {
    // this function is activated at an "onClick" event for one of the bike station links

    // step 1: request prediction information for this bikes station
    await getChartData(stationId);


    setTimeout(function() {
        // step 2: populate drop-down selection boxes where charts have
        // multiple dataSets (eg. 'bikesByHour')
        populateSelectOptions("weekDays", "bikesByHour");

        // step 3: draw charts (elemId, labels, dataPoints, dataLabels,  borderColours, fillColours)
        createChart("bikesByHour", stationPredictionData.bikesByHour.xAxisLabels, stationPredictionData.bikesByHour.dataSets.Mon, stationPredictionData.bikesByHour.seriesLabels, borderColours, fillColours);
        createChart("bikesByWeekday", stationPredictionData.bikesByWeekday.xAxisLabels, stationPredictionData.bikesByWeekday.dataSets.week, stationPredictionData.bikesByWeekday.seriesLabels, borderColours, fillColours);
    }, 500)
}

function changeHourlyGraph(day) {
    document.getElementById("bikesByHour").innerHTML = "";
    createChart("bikesByHour", stationPredictionData.bikesByHour.xAxisLabels, stationPredictionData.bikesByHour.dataSets[day], stationPredictionData.bikesByHour.seriesLabels, borderColours, fillColours);
}