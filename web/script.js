let countryCode = "AT";
let tradeType = "i";
let countriesList = [];
const importExport = document.querySelectorAll('input[name="btnradio"]');

importExport.forEach((elem) => {
  elem.addEventListener("change", function (e) {
    tradeType = elem.value;
    getChartData(countryCode, tradeType);
    e.preventDefault();
  });
});
const dropdownMenu = document.getElementById("dropdown-menu");
countriesUrl = "http://0.0.0.0:5000/countries";
fetch(countriesUrl)
  .then((resp) => resp.json())
  .then(function (data) {
    // console.log(data);
    countriesList = data;
    getChartData(countryCode, tradeType);
    Object.entries(data).forEach(([ccode, country]) => {
      const li = document.createElement("li");
      const dropdownItem = document.createElement("a");
      dropdownItem.classList.add("dropdown-item");
      dropdownItem.innerText = country;
      li.appendChild(dropdownItem);
      dropdownMenu.appendChild(li);

      dropdownItem.addEventListener(
        "click",
        function (e) {
          countryCode = ccode;
          getChartData(countryCode, tradeType);
          e.preventDefault();
        },
        false
      );
    });
  })
  .catch(function (error) {});

var ctx1 = document.getElementById("myChart1").getContext("2d");
var ctx2 = document.getElementById("myChart2").getContext("2d");
// console.log(Chart.defaults);
var myChart1 = new Chart(ctx1, {
  type: "bar",
  data: {
    labels: [],
    datasets: [
      {
        label: "Total in billion EUR",
        borderColor: "rgba(0, 13, 133, .2)",
        backgroundColor: "rgba(0, 13, 133, .2)",
        borderWidth: 1,
      },
      {
        label: "MA12",
        borderColor: "rgba(237, 29, 29, 0.85)",
        backgroundColor: "rgba(241, 196, 15,0)",
        type: "line",
        radius: 0,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      xAxes: [
        {
          stacked: true,
          type: "time",
          time: {
            displayFormats: {
              month: "YYYY",
            },
          },
        },
      ],
      yAxes: [
        {
          position: "left",
          ticks: {
            beginAtZero: true,
          },
        },
      ],
    },
    tooltips: {
      mode: "index",

      callbacks: {
        label: function (tooltipItems, data) {
          var yLabel = Number(tooltipItems.yLabel).toFixed(3) + " bill EUR";
          return yLabel;
        },
        title: function (tooltipItems, data) {
          var xLabel = tooltipItems[0].xLabel.slice(0, 4) + tooltipItems[0].xLabel.slice(7);
          return xLabel;
        },
      },
    },
  },
});
var myChart2 = new Chart(ctx2, {
  type: "bar",
  data: {
    labels: [],
    datasets: [
      {
        label: "MOM",
        borderColor: "rgba(169, 53, 192, 1)",
        backgroundColor: "rgba(169, 53, 192, 1)",
        borderWidth: 1,
      },
      {
        label: "YOY",
        borderColor: "rgba(53, 192, 174, 1)",
        backgroundColor: "rgba(53, 192, 174, 1)",
        borderWidth: 1,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      xAxes: [
        {
          stacked: true,
          type: "time",
          time: {
            displayFormats: {
              month: "YYYY",
            },
          },
        },
      ],
    },
    tooltips: {
      mode: "index",

      callbacks: {
        label: function (tooltipItems, data) {
          var yLabel = Number(tooltipItems.yLabel).toFixed(2) + "%";
          return yLabel;
        },
        title: function (tooltipItems, data) {
          var xLabel = tooltipItems[0].xLabel.slice(0, 4) + tooltipItems[0].xLabel.slice(7);
          return xLabel;
        },
      },
    },
  },
});

// getChartData(countryCode, tradeType);

function updateChart(data, labels) {
  myChart1.data.datasets[0].data = data[0];
  myChart1.data.datasets[1].data = data[1];
  myChart2.data.datasets[0].data = data[2];
  myChart2.data.datasets[1].data = data[3];
  myChart1.data.labels = labels;
  myChart2.data.labels = labels;
  myChart1.update();
  myChart2.update();
}

function getChartData(cc, tt) {
  $("#loadingMessage").html("Loading");
  document.getElementById("chart-label").innerHTML = `${countriesList[cc]} ${tt == "i" ? "Import" : "Export"}`;
  //   console.log(`Country code: ${cc}, Trade type: ${tt}`);
  $.ajax({
    url: `http://localhost:5000/data/${cc}/${tt}`,
    success: function (result) {
      $("#loadingMessage").html("");
      var data = [];
      var json = JSON.parse(result);
      data.push(Object.values(json.total).map((t) => t / 1000000000));
      data.push(Object.values(json.MA12).map((t) => (t ? t / 1000000000 : null)));
      data.push(Object.values(json.MOM));
      data.push(Object.values(json.YOY));
      var labels = Object.values(json.PERIOD).map((d) => moment(d, "YYYYMM"));

      updateChart(data, labels);
    },
    error: function (err) {
      //   console.log("error");

      $("#loadingMessage").html("Error");
    },
  });
}
