document.addEventListener("DOMContentLoaded", (_) => {
    const bodyEl = document.querySelector("body");
    
    
    function set_size(_) {
        bodyEl.style.setProperty('--window-width', bodyEl.clientWidth);
        bodyEl.style.setProperty('--window-height', bodyEl.clientHeight);
    }

    window.addEventListener("resize", e => {
        window.requestAnimationFrame(set_size);
    });
    set_size();

    document.querySelectorAll(".ajax-form").forEach(el => el.addEventListener("submit", e => {
        e.preventDefault(); 
        fetch(el.getAttribute("action"), {
            method: "post",
            body: new FormData(el),
        }).then((responseRaw) => {
            return responseRaw.text();
        }).then((response) => {
            data = JSON.parse(atob(response.replaceAll('"', '')));
            document.querySelectorAll("input").forEach( el => { el.classList.remove("error") });
            if (data['type'] == "form") {
                if (data['organization'] == false) document.querySelector("input[name='organization']").classList.add("error");
                if (data['username'] == false) document.querySelector("input[name='username']").classList.add("error");
                if (data['password'] == false) document.querySelector("input[name='password']").classList.add("error");
                if (data['name'] == false) document.querySelector("input[name='name']").classList.add("error");
                if (data['result']) {
                    document.querySelector("output#result").classList.remove('hidden');
                    document.querySelector("output#result").innerHTML = data['result'];
                } else {
                    document.querySelector("output#result").classList.add('hidden');
                }
            } else if (data['type'] == "content") {
                document.querySelector("#main-container").innerHTML = data['result'];
                setEvents();
            } else if (data['type'] == "redirect") {
                window.location = data['result'];
            }
        }).catch((error) => {
            console.log("Error submitting form", error);
        });
    }));

    document.querySelectorAll(".password-show").forEach(el => el.onclick = async e => {
        e.stopPropagation();

        el.parentElement.classList.toggle("show");

        return false;
    });

    document.querySelectorAll("#logout").forEach(el => el.onclick = async e => {
        cookieStore.delete("bearer");
        window.location = "/login";

        return false;
    });

    function setEvents() {
        document.querySelectorAll(".paste").forEach(el => el.onclick = async e => {
            el.classList.remove("clicked");
            await new Promise(r => setTimeout(r, 30));
            el.classList.add("clicked");

            try {
                await navigator.clipboard.writeText(el.dataset.paste);
              } catch (error) {
                console.error(error.message);
              }
        });
    }

    setEvents();


    if (top.location.pathname.toLocaleLowerCase() == '/vault/' || top.location.pathname.toLocaleLowerCase() == '/search/' ) {
        function generateToken(el, options) {
            window.otplib.authenticator.options = options;
            mfa = window.otplib.authenticator.generate(options['secret']);
            el.innerHTML = mfa;
            el.dataset.paste = mfa;
        }

        document.querySelectorAll("p[name='mfa']").forEach( el => {
            if (!el.dataset.otpauth) {
                el.innerHTML = "N/A";
                return;
            }

            const url = el.dataset.otpauth;
            let options = {};

            ['secret', 'algorithm'].forEach( name => {
                const r = new RegExp(`${name}=([^&]+)`).exec(url);
                if (r) {
                    options[name] = r[1].toLowerCase();
                }
            });
            ['digits', 'period'].forEach( name => {
                const r = new RegExp(`${name}=([^&]+)`).exec(url);
                if (r) {
                    options[name] = parseInt(r[1]);
                }
            });
            try {
                generateToken(el, options);
                let period = options['period'];
                setInterval(generateToken, period * 1000, el, options);
                const timerEl = el.parentElement.parentElement.querySelector('.timer');
                timerEl.style.setProperty('--duration', `${period}s`);
                timerEl.classList.remove("hidden");
            } catch (error) {
                el.innerHTML = "Invalid otpath";
            }
        });

        const modal = document.querySelector("#search-modal");
        document.querySelector("label[for='query']").addEventListener("click", (e) => {
            modal.classList.toggle("off");
        });
        modal.addEventListener("click", (e) => {modal.classList.add("off")});

        document.querySelector("#search").addEventListener("input", (e) => {
            if (e.target.value == "") {
                window.location.href = '/vault/';
            }
        });
    }
});
