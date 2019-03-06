function buildPlot(data) {
  var data = [{
    x: data.map(row => row.pos),
    y: data.map(row => -Math.log10(row.pval)),
    mode: 'markers',
    type: 'scatter',
    text: data.map(row => row.variant),
    hoverinfo: 'x+y+text+value'
  }];
  
  var layout = {
    title: `Association Summary`
  };
  
  Plotly.newPlot('plot', data, layout);
}

function init() {
  // Grab a reference to the dropdown select element
  var selector = d3.select("#selDataset");

  // Use the list of sample names to populate the select options
  d3.json("/phenotypes").then((phenotypes) => {
    phenotypes.forEach((phenotype) => {
      selector
        .append("option")
        .text(phenotype)
        .property("value", phenotype);
    });

    // Use the first sample from the list to build the initial plots
    const firstPhenotype = phenotypes[0];
    // const firstPhenoDescription = d3.json(`/manifest/${firstPhenotype}`).then((data) => data['Phenotype Description'][0]);
    // console.log(firstPhenoDescription);
    const startingChr = 1;
    const startingPos = 205874574;
    const endingPos = 205920191;

    var url = `${firstPhenotype}/${startingChr}/${startingPos}/${endingPos}`;
    d3.json(url).then(function(response) {
      data = response;
      
      // buildPlot(data);
      var myx = data.pos;
      var myy = data.pval;
      console.log(myx);
      console.log(myy);
      var mylogy = myy.map(p => -Math.log10(p));
      console.log(mylogy);
      var myyx = data.pval
      var data = [{
        x: data.pos,
        y: mylogy,
        mode: 'markers',
        type: 'scatter',
        text: data.variant,
        hoverinfo: 'x+y+text+value'
      }];
      
      var layout = {
        title: `Association Summary`
      };
      
      Plotly.newPlot('plot', data, layout);


      // buildTable(data);
    });
  });
}

function optionChanged(newPhenotype) {
  // filterButton.on("click", function() {
  //   d3.event.preventDefault();
    
  //   // Get loucs input
  //   var locusInput = d3.select("#locus").property("value");
  // }
}

// Initialize the dashboard
init();
