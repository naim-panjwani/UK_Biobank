function buildPlot(pos, pval, variant, minor_AF, phenoDescription) {
  var data = [{
    x: pos,
    y: pval.map(p => -Math.log10(p)),
    mode: 'markers',
    type: 'scatter',
    text: variant,
    hoverinfo: 'x+y+text+value'
  }];
  
  var layout = {
    title: `Association Summary for: ${phenoDescription}`
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
    d3.json(url).then(function(data) {
      //console.log(data);
      buildPlot(data.pos, data.pval, data.variant, data.minor_AF);
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
