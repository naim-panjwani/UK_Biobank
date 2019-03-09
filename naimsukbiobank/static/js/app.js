const startingChr = 1;
const startingPos = 205500000;
const endingPos = 206000000;
const genomicWindowLimit = 2e6;
var submitButton = d3.select("#submit-btn");
var errorDiv = d3.select("#error-messages");

d3.select("#locusText").text(`Enter Genomic Coordinates (window limit: ${genomicWindowLimit/1e6} Mbp)`);
d3.select("#locus").attr('placeholder', `${startingChr}:${startingPos}-${endingPos}`);

function getPhenotypeDescription(phenotype) {
  //console.log(phenotype);
  var url = `phenotype/${phenotype}`
  var descr;

  d3.json(url).then(response => {
    response.description[0];
  });
}

function buildPlot(data, phenodesc) {
  var myx = data.pos;
  var myy = data.pval;
  var mylogy = myy.map(p => -Math.log10(p));
  var metadata = data.rsid;
  var chr = data.chr[0];
  var chromText = "";
  if(chr === 23) {chromText="X"} else {chromText=chr.toString()}
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
        size: 14
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
}

function buildTable(data) {
  var tbody = d3.select("#variants-table").select("tbody");
  
  // Clear table:
  tbody.text("")

  // Desired column headers:
  var desired_columns = ['chr', 'pos', 'rsid', 'minor_AF', 'consequence', 'consequence_category', 'beta', 'pval'];

  // Add table body:
  for(i=0; i<data[desired_columns[0]].length; i++) { // for each variant
    var row = tbody.append('tr');
    for(j=0; j<desired_columns.length; j++) { // for each column
      row.append('td').text(data[desired_columns[j]][i]);
    }
  }

  // var sortAscending = true;
  // var titles = desired_columns;
  // var headers = table.append('thead').append('tr')
  //                  .selectAll('th')
  //                  .data(titles).enter()
  //                  .append('th')
  //                  .text(function (d) {
  //                     return d;
  //                   })
  //                  .on('click', function (d) {
  //                    headers.attr('class', 'header');
                     
  //                    if (sortAscending) {
  //                      rows.sort(function(a, b) { return b[d] < a[d]; });
  //                      sortAscending = false;
  //                      this.className = 'aes';
  //                    } else {
  //                    rows.sort(function(a, b) { return b[d] > a[d]; });
  //                    sortAscending = true;
  //                    this.className = 'des';
  //                    }
                     
  //                  });
  
  // var rows = table.append('tbody').selectAll('tr')
  //              .data(data[desired_columns[0]]).enter()
  //              .append('tr');
  // rows.selectAll('td')
  //   .data(function (d) {
  //     return titles.map(function (k) {
  //       return { 'value': d[k], 'name': k};
  //     });
  //   }).enter()
  //   .append('td')
  //   .attr('data-th', function (d) {
  //     return d.name;
  //   })
  //   .text(function (d) {
  //     return d.value;
  //   });
}

function showData(phenotype, chr, startbp, endbp) {
  var url = `assoc/${phenotype}/${chr}/${startbp}/${endbp}`;
  d3.json(url).then(response => {
    data = response;
    d3.json(`phenotype/${phenotype}`).then(phenoresponse => {
      var phenodesc = phenoresponse.Phenotype_description[0];
      //console.log(phenodesc);
      buildPlot(data, phenodesc);
      buildTable(data);
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
    showData(firstPhenotype, startingChr, startingPos, endingPos);
  });
}


// If another phenotype is selected
function optionChanged(newPhenotype) {  
  // Clear any error messages
  errorDiv.text("")

  // Fetch new data each time a new phenotype is selected
  // Get locus input - if any
  var locusInput = d3.select("#locus").property("value");
  if(locusInput) {
    var chrom = parseInt(locusInput.split(":",1));
    var startbase = parseInt(locusInput.split('-')[0].split(":")[1]);
    var endbase = parseInt(locusInput.split('-')[1]);
    
    if(chrom && startbase && endbase) {
      if((endbase - startbase) > genomicWindowLimit) {
        errorDiv.text(`Please query a genomic region less than ${genomicWindowLimit/1e6} Mbp`)
      } else if (startbase > endbase) {
        errorDiv.text("Starting basepair position is greater than ending position")
      } else {
        showData(newPhenotype, chrom, startbase, endbase)
      }
    } else {
      showData(newPhenotype, startingChr, startingPos, endingPos);
    }
  } else {
    showData(newPhenotype, startingChr, startingPos, endingPos);
  }
}



// Listen for submit event
submitButton.on("click", function() {
  d3.event.preventDefault();
  
  // Get new phenotype (if applicable)
  var selector = d3.select("#selDataset");
  var pheno = selector.property("value");

  // Clear any error messages
  errorDiv.text("")

  // Get locus input
  var locusInput = d3.select("#locus").property("value");
  if(locusInput) {
    var chrom = parseInt(locusInput.split(":",1));
    var startbase = parseInt(locusInput.split('-')[0].split(":")[1]);
    var endbase = parseInt(locusInput.split('-')[1]);
    
    if(chrom && startbase && endbase) {
      if((endbase - startbase) > genomicWindowLimit) {
        errorDiv.text(`Please query a genomic region less than ${genomicWindowLimit/1e6} Mbp`)
      } else if (startbase > endbase) {
        errorDiv.text("Starting basepair position is greater than ending position")
      } else {
        showData(pheno, chrom, startbase, endbase);
      }
    } else {
      errorDiv.text(`Please enter a valid position (eg.${startingChr}:${startingPos}-${endingPos})`)
    }
  }
  
});

// Initialize the dashboard
init();
