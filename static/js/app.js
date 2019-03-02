function buildMetadata(phenotype, chr, startbp, endbp) {

  // @TODO: Complete the following function that builds the metadata panel

  // Use `d3.json` to fetch the metadata for a sample
  var url = `/metadata/${phenotype}/${chr}/${startbp}/${endbp}`;
  d3.json(url).then(function(response) {
    //console.log(response);
    metadata = response;
    // Use d3 to select the panel with id of `#sample-metadata`
    var sampleMetadataDiv = d3.select("#sample-metadata");
    // Use `.html("") to clear any existing metadata
    sampleMetadataDiv.html("");
    // Use `Object.entries` to add each key and value pair to the panel
    // Hint: Inside the loop, you will need to use d3 to append new
    // tags for each key-value in the metadata.
    Object.entries(metadata).forEach(([key, value]) => {
      sampleMetadataDiv.append("h6").text(`${key}: ${value}`);
    });
    // BONUS: Build the Gauge Chart
    buildGauge(metadata.WFREQ);
  });
}

function buildCharts(sample) {

  // @TODO: Use `d3.json` to fetch the sample data for the plots
  var url = `/samples/${sample}`;
  d3.json(url).then(function(response) {
    // @TODO: Build a Pie Chart
    // HINT: You will need to use slice() to grab the top 10 sample_values,
    // otu_ids, and labels (10 each).

    // Need to transform the response to an array of objects in order to sort and obtain the top 10 sample_values:
    function zip(arrays) {
      return arrays[0].map(function(_,i){
        return arrays.map(function(array){return array[i]})
        });
    }
    zipped_response = zip([response.otu_ids, response.otu_labels, response.sample_values]);
    response_objects = [];
    for(var i = 0; i < zipped_response.length; i++) {
      response_objects.push({
        'otu_ids': zipped_response[i][0],
        'otu_labels': zipped_response[i][1],
        'sample_values': zipped_response[i][2]
      });
    }
    response_objects.sort(function (a, b) {
      return b.sample_values - a.sample_values;
    });
    var top10 = response_objects.slice(0,10);
    //console.log(top10.map(row => row.otu_labels));
    var data = [{
      values: top10.map(row => row.sample_values),
      labels: top10.map(row => row.otu_ids),
      type: 'pie',
      hovertext: top10.map(row => row.otu_labels),
      hoverinfo: 'label+percent+text+value',
      textinfo: 'none'
    }];
    
    var layout = {
      title: `OTU Composition for Sample ${sample}`
    };
    
    Plotly.newPlot('pie', data, layout);


    // @TODO: Build a Bubble Chart using the sample data
    // I am going to assume that here we want to see all samples...?
    var trace1 = {
      x: response_objects.map(row => row.otu_ids),
      y: response_objects.map(row => row.sample_values),
      text: response_objects.map(row => row.otu_labels),
      mode: 'markers',
      marker: {
        color: response_objects.map(row => row.otu_ids),
        size: response_objects.map(row => row.sample_values)
      },
      hoverinfo: 'x+y+text'
    };
    
    var data = [trace1];
    
    var layout = {
      title: `OTU Values for Sample ${sample}`,
      xaxis: {title: {text: 'OTU ID'}},
      yaxis: {title: {text: 'Sample Values'}},
      showlegend: false
    };
    
    Plotly.newPlot('bubble', data, layout);

  });
}

function init() {
  // Grab a reference to the dropdown select element
  var selector = d3.select("#selDataset");

  // Use the list of sample names to populate the select options
  d3.json("/names").then((sampleNames) => {
    sampleNames.forEach((sample) => {
      selector
        .append("option")
        .text(sample)
        .property("value", sample);
    });

    // Use the first sample from the list to build the initial plots
    const firstSample = sampleNames[0];
    buildCharts(firstSample);
    buildMetadata(firstSample);
  });
}

function optionChanged(newSample) {
  // Fetch new data each time a new sample is selected
  buildCharts(newSample);
  buildMetadata(newSample);
}

// Initialize the dashboard
init();
