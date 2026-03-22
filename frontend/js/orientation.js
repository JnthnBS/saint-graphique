// Fonction pour vérifier l'orientation (avec blocage des réactivations)
let isPopupClosedManually = false; // Variable pour suivre si la popup a été fermée manuellement

function checkOrientation() {
  const popup = document.getElementById('landscapePopup');

  // Si la popup a été fermée manuellement, ne pas la réactiver
  if (isPopupClosedManually) {
    return;
  }

  const isMobilePortrait = window.matchMedia("(orientation: portrait)").matches &&
                          /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

  if (isMobilePortrait) {
    popup.style.display = 'flex';
  } else {
    popup.style.display = 'none';
  }
}

// Fonction pour fermer la popup (bouton "Continuer en portrait")
function closePopup() {
  const popup = document.getElementById('landscapePopup');
  if (popup) {
    popup.style.display = 'none';
    isPopupClosedManually = true; // Bloque la réactivation automatique
    console.log("Popup fermée manuellement");
  }
}

// Fonction pour le bouton "Passer en paysage"
function handleLandscapeClick() {
  isPopupClosedManually = false; // Réactive la vérification automatique

  // Supprimer un message précédent s'il existe
  const existingMessage = document.getElementById('guideMessage');
  if (existingMessage) {
    document.body.removeChild(existingMessage);
  }

  // Créer un nouveau message temporaire
  const guideMessage = document.createElement('div');
  guideMessage.id = 'guideMessage';
  guideMessage.style.position = 'fixed';
  guideMessage.style.bottom = '20px';
  guideMessage.style.left = '50%';
  guideMessage.style.transform = 'translateX(-50%)';
  guideMessage.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
  guideMessage.style.color = 'white';
  guideMessage.style.padding = '10px 20px';
  guideMessage.style.borderRadius = '4px';
  guideMessage.style.zIndex = '9998';
  guideMessage.textContent = "🔄 Tournez votre appareil en paysage";

  document.body.appendChild(guideMessage);

  // Supprimer le message après 3 secondes
  setTimeout(() => {
    if (guideMessage) document.body.removeChild(guideMessage);
  }, 3000);
}

// Initialisation
checkOrientation();
window.addEventListener('resize', checkOrientation);
