function buildPlot(phenotype, chr, startbp, endbp) {

  var url = `assoc/${phenotype}/${chr}/${startbp}/${endbp}`;
  d3.json(url).then(response => {

    //if (error) throw error;

    data = response;
    console.log(data)
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
  });
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
    // const firstPhenoDescription = d3.json(`/${firstPhenotype}`).then((data) => data['Phenotype Description'][0]);
    // console.log(firstPhenoDescription);
    const startingChr = 1;
    const startingPos = 700000;
    const endingPos = 800000;
    buildPlot(firstPhenotype, startingChr, startingPos, endingPos)
    // buildTable(data);
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
