document.getElementById('send-requests').addEventListener('click', function() {
    const requests = Array.from(document.querySelectorAll('.search-bar')).map(bar => {
        return {
            commune: bar.querySelector('select[id^="commune"]').value.split('(')[1].replace(')', ''),
            sexe: bar.querySelector('select[id^="sexe"]').value,
            objet: bar.querySelector('select[id^="objet"]').value,
            annee: bar.querySelector('select[id^="annee"]').value,
	    width: svgContainer.clientWidth
        };
    });

    // const svgContainer = document.getElementById('svgContainer');
    // const width = svgContainer.clientWidth;

    // const payload = {
    //     requests: requests,
    //     width: width
    // };
    console.log(requests)
    var config = {

	toImageButtonOptions: {

	    format: 'png',
	    filename: 'saint-graphique',
	    height: 1440,
	    width: 1920,
	    scale: 1
	}

};
    fetch('/api/graph', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requests)
    })
        .then(response => response.json())
        .then(plotlyJson => {
            Plotly.newPlot(
                'svgContainer',
                JSON.parse(plotlyJson).data,
                JSON.parse(plotlyJson).layout,
		config
            );
        })
        .catch(error => console.error("Erreur:", error));
});
