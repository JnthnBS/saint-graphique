document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('search-bars-container');
    const addButton = document.getElementById('add-bar')
    Array.from(container.children).forEach(bar => {
	addSuggestionsContainerToBar(bar);
    });
    Array.from(container.children).forEach(bar => {
	addAnneesContainerToBar(bar);
    });
    Array.from(container.children).forEach(bar => {
	addSexesContainerToBar(bar);
    });
    // Fonction pour charger les années disponibles en fonction de l'objet sélectionné
    async function loadAnnees(objetId) {
	try {
            if (objetId === "population") {
		return ["2022"];
            } else if (objetId === "presidentielles") {
		return ["2022", "2017"];
            } else if (objetId === "europeennes") {
		return ["2024", "2019"];
            } else if (objetId === "legislatives") {
		return ["2024", "2022", "2017"];
            } else {
		return ["2022"];
            }
	} catch (error) {
            console.error(`Erreur lors du chargement des années pour l'objet ${objectType}:`, error);
            return [];
	}
    }
    // Fonction pour charger les sexes disponibles en fonction de l'objet sélectionné
    async function loadSexes(objetId) {
	try {
            if (objetId === "population") {
		return [
		    { value: 1, text: "Tous" },
		    { value: 2, text: "Hommes" },
		    { value: 3, text: "Femmes" }
		];
            } else if (objetId === "presidentielles") {
		return [{value: 1, text: "Tous"}];
            } else if (objetId === "europeennes") {
		return [{value: 1, text: "Tous"}];
            } else if (objetId === "legislatives") {
		return [{value: 1, text: "Tous"}];
            } else {
		return [{value: 1, text: "Tous"}];
            }
	} catch (error) {
            console.error(`Erreur lors du chargement des années pour l'objet ${objectType}:`, error);
            return [];
	}
    }
    // Fonction pour charger les années dans le select
    async function addAnneesContainerToBar(bar) {
	const objetSelect = bar.querySelector('[data-action="objet"]');
	const anneeSelect = bar.querySelector('.annee-select');
	anneeSelect.innerHTML = '<option value="">Sélectionnez une année...</option>';
	objetSelect.addEventListener('change', async function() {
	    anneeSelect.innerHTML = '';
            const objetId = this.value;
            const annees = await loadAnnees(objetId);
            annees.forEach(annee => {
		const option = document.createElement('option');
		option.value = annee;
		option.textContent = annee;
		anneeSelect.appendChild(option);
            });
	    anneeSelect.disabled = false;
	});
    }
    // Fonction pour charger les sexes dans le select
    async function addSexesContainerToBar(bar) {
	const objetSelect = bar.querySelector('[data-action="objet"]');
	const sexesSelect = bar.querySelector('.sexes-select');
	sexesSelect.innerHTML = '<option value="">Sélectionnez un genre...</option>';
	objetSelect.addEventListener('change', async function() {
	    sexesSelect.innerHTML = '';
            const objetId = this.value;
            const sexes = await loadSexes(objetId);
            sexes.forEach(sexes => {
		const option = document.createElement('option');
		option.value = sexes.value;
		option.textContent = sexes.text;
		sexesSelect.appendChild(option);
            });
	    sexesSelect.disabled = false;
	});
    }    
    // Fonction pour charger les communes dans le select
    async function addSuggestionsContainerToBar(bar) {
	const departementSelect = bar.querySelector('[data-action="departement"]');
	const communeSelect = bar.querySelector('.commune-select');
	communeSelect.innerHTML = '<option value="">Sélectionnez une commune...</option>';
	departementSelect.addEventListener('change', async function() {
	    communeSelect.innerHTML = '';
            const departementId = this.value;
            const communes = await loadCommunes(departementId);
            communes.forEach(commune => {
		const option = document.createElement('option');
		option.value = commune;
		option.textContent = commune;
		communeSelect.appendChild(option);
            });
	    communeSelect.disabled = false;
	});
    }
    // Fonction pour initialiser les listes de commune
    async function loadCommunes(departementId) {
	try {
            const response = await fetch(`geo/${departementId}_communes.txt`);
            const communes = await response.text();
            return communes.split('\n').filter(commune => commune.trim() !== '');
	} catch (error) {
            console.error(`Erreur lors du chargement des communes pour le département ${departementId}:`, error);
            return [];
	}
    }
    // Fonction pour mettre à jour l'état du bouton d'ajout
    function updateAddButtonState() {
        const currentBars = container.children.length;
        if (currentBars >= 5) {
            addButton.style.display = 'none'; // Masquer le bouton
        } else {
            addButton.style.display = ''; // Réafficher le bouton
        }
    }

    // Ajouter une nouvelle barre
    addButton.addEventListener('click', function() {
        if (container.children.length === 0) {
            console.error("Aucune barre existante pour cloner.");
            return;
        }

        const lastBar = container.lastElementChild;
        const newBar = lastBar.cloneNode(true);

        // Incrémenter les IDs
        const barId = parseInt(lastBar.id.replace('search-bar-', '')) + 1;
        newBar.id = `search-bar-${barId}`;

        newBar.querySelectorAll('[id]').forEach(el => {
            el.id = el.id.replace(/\d+$/, barId);
        });

        // Montrer le bouton de suppression
        newBar.querySelector('.remove-bar').classList.remove('d-none');

        container.appendChild(newBar);
	addSuggestionsContainerToBar(newBar);
	addAnneesContainerToBar(newBar);
	addSexesContainerToBar(newBar);	
        updateAddButtonState();
    });

    // Supprimer une barre
    container.addEventListener('click', function(e) {
        if (e.target.closest('[data-action="remove"]')) {
            const searchBar = e.target.closest('.search-bar');
            if (searchBar) {
                searchBar.remove();
                updateAddButtonState();
            }
        }
    });

    // Initialiser l'état du bouton au chargement
    updateAddButtonState();

    // Ajouter les suggestions aux barres existantes
    Array.from(container.children).forEach(bar => {
        addSuggestionsContainerToBar(bar);
    });
});

