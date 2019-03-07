
var submitButton = d3.select("#submit-btn")

function getPhenotypeDescription(phenotype) {
  console.log(phenotype);
  var url = `phenotype/${phenotype}`
  var descr;

  d3.json(url).then(response => {
    response.description[0];
  });
}

function buildPlot(phenotype, chr, startbp, endbp) {

  var url = `assoc/${phenotype}/${chr}/${startbp}/${endbp}`;
  d3.json(url).then(response => {
    data = response;
    // console.log(data)
    var myx = data.pos;
    var myy = data.pval;
    // console.log(myx);
    // console.log(myy);
    var mylogy = myy.map(p => -Math.log10(p));
    // console.log(mylogy);
    var chromText = "";
    if(chr === 23) {chromText="X"} else {chromText=chr.toString()}
    var metadata = data.rsid;
    d3.json(`phenotype/${phenotype}`).then(phenoresponse => {
      var phenodesc = phenoresponse.description[0];

      var data = [{
        x: myx,
        y: mylogy,
        mode: 'markers',
        type: 'scatter',
        text: metadata,
        hoverinfo: 'x+y+text+value'
      }];
      
      var layout = {
        title: {
          text: `Association Summary<br>${phenodesc}`,
          font: {
            family: 'Courier New, monospace',
            size: 24
          },
        },
        xaxis: {
          title: {
            text: `chr${chromText} genomic region`,
            font: {
              family: 'Courier New, monospace',
              size: 18,
              color: '#7f7f7f'
            }
          },
        },
        yaxis: {
          title: {
            text: `-log10(p-value)`,
            font: {
              family: 'Courier New, monospace',
              size: 18,
              color: '#7f7f7f'
            }
          }
        }
      };
      
      Plotly.newPlot('plot', data, layout);
    });
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
    buildPlot(firstPhenotype, startingChr, startingPos, endingPos);
    // buildTable(firstPhenotype, startingChr, startingPos, endingPos);
  });
}


// Listen for submit event
submitButton.on("click", function() {
  d3.event.preventDefault();
  
  // Get new phenotype (if applicable)
  var selector = d3.select("#selDataset");
  var pheno = selector.property("value");
  var errorDiv = d3.select("#error-messages")

  // Clear any error messages
  errorDiv.text("")

  // Get locus input
  var locusInput = d3.select("#locus").property("value");
  if(locusInput) {
    var chrom = parseInt(locusInput.split(":",1));
    var startbase = parseInt(locusInput.split('-')[0].split(":")[1]);
    var endbase = parseInt(locusInput.split('-')[1]);
    
    if(chrom && startbase && endbase) {
      if((endbase - startbase) > 100000) {
        errorDiv.text("Please query a genomic region less than 100kbp")
      } else if (startbase > endbase) {
        errorDiv.text("Starting position is greater than ending position")
      } else {
        buildPlot(pheno, chrom, startbase, endbase);
      }
      // buildTable(pheno, chrom, startbase, endbase)
    } else {
      errorDiv.text("Please enter a genomic region")
    }
  }
  
});

// Initialize the dashboard
init();
