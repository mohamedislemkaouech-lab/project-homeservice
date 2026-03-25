// static/js/chatbot.js
// Pure vanilla-JS chatbot for ServicesDOM.
// All answers are computed in the browser — no server calls, no API keys required.
// Uses a keyword-based intent engine with rich French responses.

document.addEventListener('DOMContentLoaded', function () {

    // ── DOM refs ──────────────────────────────────────────────────────────────
    const toggleBtn    = document.getElementById('chatbot-toggle');
    const chatWindow   = document.getElementById('chatbot-window');
    const closeBtn     = document.getElementById('chatbot-close');
    const inputField   = document.getElementById('chatbot-input');
    const sendBtn      = document.getElementById('chatbot-send');
    const msgContainer = document.getElementById('chatbot-messages');

    if (!toggleBtn || !chatWindow) return;

    // ── Knowledge base ────────────────────────────────────────────────────────
    // Each entry: { patterns: [string], response: string | fn → string }
    const KB = [
        // Greetings
        {
            patterns: ['bonjour', 'salut', 'hello', 'bonsoir', 'coucou', 'hi ', 'hey'],
            response: "Bonjour ! 😊 Je suis l'assistant ServicesDOM. Je peux vous aider à :\n• Trouver un prestataire\n• Comprendre comment réserver\n• Connaître les tarifs\n• Gérer votre compte\n\nQue souhaitez-vous faire ?"
        },
        // Services - Baby-sitting
        {
            patterns: ['baby', 'bébé', 'enfant', 'garde', 'garderie', 'babysit'],
            response: "👶 **Baby-sitting**\nNous disposons de baby-sitters sérieux et attentionnés. Ils proposent :\n• Garde à domicile\n• Aide aux devoirs\n• Activités ludiques\n• Horaires flexibles\n\nPour trouver un baby-sitter, cliquez sur l'onglet *Baby-sitting* sur la page d'accueil !"
        },
        // Services - Ménage
        {
            patterns: ['ménage', 'menage', 'nettoyage', 'nettoyer', 'propre', 'femme de ménage'],
            response: "🧹 **Ménage**\nNos professionnels du ménage interviennent pour :\n• Nettoyage de maisons et appartements\n• Bureaux et locaux commerciaux\n• Nettoyage régulier ou ponctuel\n• Produits sûrs et efficaces\n\nConsultez les prestataires disponibles sur la page *Ménage* !"
        },
        // Services - Jardinage
        {
            patterns: ['jardin', 'jardinage', 'tonte', 'pelouse', 'haie', 'plante', 'taille'],
            response: "🌿 **Jardinage**\nNos jardiniers professionnels s'occupent de :\n• Tonte de pelouse\n• Taille de haies et arbustes\n• Plantation et entretien\n• Nettoyage d'espaces verts\n\nTrouvez votre jardinier sur la page *Jardinage* !"
        },
        // Services - Plomberie
        {
            patterns: ['plombier', 'plomberie', 'fuite', 'tuyau', 'robinet', 'eau', 'canalisation', 'wc', 'toilette'],
            response: "🔧 **Plomberie**\nNos plombiers qualifiés interviennent pour :\n• Réparation de fuites\n• Installation de robinets et sanitaires\n• Débouchage de canalisations\n• Urgences plomberie 24h/24\n\nTrouvez un plombier disponible sur la page *Plomberie* !"
        },
        // Services - Électricité
        {
            patterns: ['electricien', 'électricien', 'électricité', 'electricite', 'circuit', 'prise', 'lumière', 'lumiere', 'panne'],
            response: "⚡ **Électricité**\nNos électriciens certifiés réalisent :\n• Installation et câblage électrique\n• Réparation de pannes\n• Mise aux normes\n• Pose de prises, interrupteurs, luminaires\n\nConsultez les électriciens disponibles sur la page *Électricité* !"
        },
        // Services - Climatisation
        {
            patterns: ['clim', 'climatisation', 'climatiseur', 'froid', 'chaleur', 'chauffage', 'ventilation'],
            response: "❄️ **Climatisation**\nNos techniciens en climatisation proposent :\n• Installation de climatiseurs\n• Entretien annuel obligatoire\n• Réparation de pannes\n• Recharge en gaz réfrigérant\n\nTrouvez un technicien sur la page *Climatisation* !"
        },
        // Services - Peinture
        {
            patterns: ['peinture', 'peindre', 'peintre', 'mur', 'facades', 'façade', 'intérieur', 'extérieur'],
            response: "🎨 **Peinture**\nNos peintres professionnels réalisent :\n• Peinture intérieure (murs, plafonds, portes)\n• Peinture extérieure et façades\n• Préparation et prétraitement des surfaces\n• Finitions soignées et durables\n\nChoisissez votre peintre sur la page *Peinture* !"
        },
        // Services - Déménagement
        {
            patterns: ['déménag', 'demenag', 'transport', 'camion', 'carton', 'emball', 'déménagement'],
            response: "🚚 **Déménagement**\nNos équipes de déménagement vous proposent :\n• Emballage sécurisé de vos affaires\n• Transport par camion adapté\n• Déménagements résidentiels et professionnels\n• Montage/démontage de meubles\n\nRéservez votre déménagement sur la page *Déménagement* !"
        },
        // How to reserve
        {
            patterns: ['réserv', 'reserv', 'comment', 'prendre rendez', 'rdv', 'rendez-vous', 'contacter'],
            response: "📅 **Comment réserver ?**\n1. Choisissez la catégorie de service souhaitée\n2. Consultez les profils des prestataires disponibles\n3. Cliquez sur *Contacter* ou *Voir les détails*\n4. Choisissez une date et un créneau horaire\n5. Confirmez votre réservation\n\nLe prestataire recevra votre demande et pourra l'accepter. Vous serez notifié par message !"
        },
        // Prices
        {
            patterns: ['prix', 'tarif', 'coût', 'cout', 'combien', 'facturation', 'paiement', 'cher'],
            response: "💰 **Tarifs**\nLes tarifs sont fixés librement par chaque prestataire et varient selon :\n• Le type de service\n• La durée de l'intervention\n• La localisation\n• L'expérience du prestataire\n\nVous pouvez comparer les prix directement sur la page de chaque service et filtrer par fourchette de prix !"
        },
        // Account / Registration
        {
            patterns: ['compte', 'inscription', 'inscrire', 'créer', 'creer', 'profil', 'connexion', 'connecter', 's\'inscrire', 'enregistr'],
            response: "👤 **Créer un compte**\nNous proposons deux types de comptes :\n\n• **Client** : Recherchez et réservez des services à domicile\n• **Prestataire** : Proposez vos services et gérez vos réservations\n\nCliquez sur *Connexion / S'inscrire* en haut de la page et suivez les étapes. C'est gratuit et rapide !"
        },
        // Rating / Reviews
        {
            patterns: ['avis', 'note', 'étoile', 'etoile', 'notation', 'évaluer', 'evaluer', 'commentaire', 'satisfaction'],
            response: "⭐ **Avis et évaluations**\nAprès chaque prestation terminée, vous pouvez :\n• Attribuer une note de 1 à 5 étoiles\n• Laisser un commentaire détaillé\n• Aider d'autres utilisateurs à choisir\n\nLes avis sont vérifiés et ne peuvent pas être modifiés par les prestataires. La transparence est notre priorité !"
        },
        // About ServicesDOM
        {
            patterns: ['c\'est quoi', 'qu\'est-ce', 'plateforme', 'servicesdom', 'service dom', 'à propos', 'a propos', 'qui êtes', 'qui etes'],
            response: "🏠 **À propos de ServicesDOM**\nServicesDOM est une plateforme tunisienne de mise en relation entre :\n• Des particuliers cherchant des professionnels fiables\n• Des prestataires qualifiés souhaitant développer leur activité\n\nNos catégories : Baby-sitting, Climatisation, Déménagement, Jardinage, Ménage, Peinture, Plomberie et Électricité.\n\nNotre mission : vous faciliter la vie au quotidien !"
        },
        // Thanks
        {
            patterns: ['merci', 'thanks', 'remercie', 'super', 'parfait', 'génial', 'nickel'],
            response: "😊 De rien ! C'est un plaisir de vous aider. N'hésitez pas si vous avez d'autres questions. Bonne journée !"
        },
        // Goodbye
        {
            patterns: ['au revoir', 'bye', 'bonne journée', 'bonne soiree', 'à bientôt', 'salut'],
            response: "👋 À bientôt sur ServicesDOM ! N'hésitez pas à revenir si vous avez besoin d'aide."
        },
        // Help
        {
            patterns: ['aide', 'help', 'problème', 'probleme', 'question', 'sais pas', 'comprends pas'],
            response: "🤝 **Je peux vous aider avec :**\n• 🔍 Trouver un service (ex: 'je cherche un plombier')\n• 📅 Comprendre comment réserver ('comment réserver ?')\n• 💰 Les tarifs ('quels sont les prix ?')\n• 👤 Créer un compte ('comment s'inscrire ?')\n• ⭐ Les avis ('comment laisser un avis ?')\n• 🏠 La plateforme ('c'est quoi ServicesDOM ?')\n\nQue puis-je faire pour vous ?"
        },
    ];

    // Default response when no intent matched
    const DEFAULT_RESPONSE = "Je n'ai pas bien compris votre question 🤔\n\nVoici ce que je peux faire :\n• Trouver un service (ex: 'je cherche un plombier')\n• Expliquer comment réserver\n• Renseigner sur les tarifs\n• Aider à créer un compte\n\nPosez votre question différemment ou tapez *aide* pour voir toutes mes options !";

    // ── Intent matching ───────────────────────────────────────────────────────
    function getResponse(message) {
        const lc = message.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        for (const entry of KB) {
            if (entry.patterns.some(p => lc.includes(p.normalize('NFD').replace(/[\u0300-\u036f]/g, '')))) {
                return typeof entry.response === 'function' ? entry.response(lc) : entry.response;
            }
        }
        return DEFAULT_RESPONSE;
    }

    // ── Open / close ──────────────────────────────────────────────────────────
    toggleBtn.addEventListener('click', function () {
        chatWindow.classList.add('chatbot-open');
        chatWindow.classList.remove('chatbot-closed', 'd-none');
        toggleBtn.classList.add('d-none');
        inputField.focus();
    });

    closeBtn.addEventListener('click', function () {
        chatWindow.classList.add('chatbot-closed');
        chatWindow.classList.remove('chatbot-open');
        toggleBtn.classList.remove('d-none');
        setTimeout(function () { chatWindow.classList.add('d-none'); }, 300);
    });

    // ── Send logic ────────────────────────────────────────────────────────────
    function sendMessage() {
        const text = inputField.value.trim();
        if (!text) return;

        inputField.value = '';
        appendBubble(text, 'user');

        // Simulate thinking with a short delay + typing dots
        const typingEl = appendTypingIndicator();

        setTimeout(function () {
            typingEl.remove();
            const reply = getResponse(text);
            appendBubble(reply, 'bot');
        }, 600 + Math.random() * 400);
    }

    // ── Helpers ───────────────────────────────────────────────────────────────
    function appendBubble(text, sender) {
        const wrap = document.createElement('div');
        wrap.className = 'chat-message ' + (sender === 'user' ? 'user-message' : 'bot-message');

        const bubble = document.createElement('div');
        bubble.className = 'bubble';

        // Render **bold** markdown
        bubble.innerHTML = text
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');

        wrap.appendChild(bubble);
        msgContainer.appendChild(wrap);
        scrollToBottom();
        return wrap;
    }

    function appendTypingIndicator() {
        const wrap = document.createElement('div');
        wrap.className = 'chat-message bot-message';
        wrap.innerHTML = '<div class="bubble typing-dots"><span></span><span></span><span></span></div>';
        msgContainer.appendChild(wrap);
        scrollToBottom();
        return wrap;
    }

    function scrollToBottom() {
        msgContainer.scrollTop = msgContainer.scrollHeight;
    }

    // ── Event listeners ───────────────────────────────────────────────────────
    sendBtn.addEventListener('click', sendMessage);

    inputField.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});
