const initializeAsyncAuthForm = ({ form, reducedMotion, navigate }) => {
    if (!form) {
        return;
    }

    const submitButton = form.querySelector("[data-auth-submit]");
    const statusNode = form.parentElement?.querySelector("[data-auth-status]") || form.querySelector("[data-auth-status]");
    const resultNode = form.parentElement?.querySelector("[data-auth-result]") || form.querySelector("[data-auth-result]");
    const resultFoundNode = resultNode?.querySelector("[data-auth-result-found]") || null;
    const resultTitle = resultNode?.querySelector("[data-auth-result-title]") || null;
    const resultMessage = resultNode?.querySelector("[data-auth-result-message]") || null;
    const resultLink = resultNode?.querySelector("[data-auth-result-link]") || null;
    const liveFieldErrors = new Map(
        [...form.querySelectorAll("[data-auth-field-error]")].map((node) => [node.dataset.authFieldError, node])
    );

    const defaultButtonLabel = submitButton?.textContent?.trim() || "Submit";
    const busyLabel = submitButton?.dataset.authButtonBusy || form.dataset.authButtonBusy || "Submitting...";
    const successMode = form.dataset.authSuccess || "redirect";
    let isSubmitting = false;

    const setStatus = ({ title = "", message = "", tone = "error" } = {}) => {
        if (!statusNode) {
            return;
        }

        if (!title && !message) {
            statusNode.hidden = true;
            statusNode.classList.remove("is-error", "is-info", "is-success");
            statusNode.innerHTML = "";
            return;
        }

        statusNode.hidden = false;
        statusNode.classList.remove("is-error", "is-info", "is-success");
        statusNode.classList.add(`is-${tone}`);
        statusNode.innerHTML = `${title ? `<strong>${title}</strong>` : ""}${message ? `<p>${message}</p>` : ""}`;
    };

    const clearFieldError = (fieldName) => {
        const field = form.elements.namedItem(fieldName);
        if (field instanceof HTMLElement) {
            field.classList.remove("is-invalid");
            field.removeAttribute("aria-invalid");
        }

        const errorNode = liveFieldErrors.get(fieldName);
        if (errorNode) {
            errorNode.hidden = true;
            errorNode.textContent = "";
            errorNode.classList.remove("is-visible");
        }
    };

    const clearAllFieldErrors = () => {
        liveFieldErrors.forEach((_, fieldName) => clearFieldError(fieldName));
    };

    const setFieldError = (fieldName, message = "") => {
        const field = form.elements.namedItem(fieldName);
        if (field instanceof HTMLElement) {
            field.classList.add("is-invalid");
            field.setAttribute("aria-invalid", "true");
        }

        const errorNode = liveFieldErrors.get(fieldName);
        if (errorNode && message) {
            errorNode.hidden = false;
            errorNode.textContent = message;
            errorNode.classList.add("is-visible");
        }
    };

    const hideResult = () => {
        if (resultNode) {
            resultNode.hidden = true;
        }
        if (resultFoundNode) {
            resultFoundNode.hidden = true;
        }
    };

    const showResult = (result) => {
        if (!resultNode || !result) {
            return;
        }

        resultNode.hidden = false;
        if (resultFoundNode) {
            resultFoundNode.hidden = !result.visible;
        }

        if (resultTitle) {
            resultTitle.textContent = result.title || "";
        }
        if (resultMessage) {
            resultMessage.textContent = result.message || "";
        }
        if (resultLink) {
            const hasLink = Boolean(result.link_url);
            resultLink.hidden = !hasLink;
            if (hasLink) {
                resultLink.href = result.link_url;
            }
            if (result.link_label) {
                resultLink.textContent = result.link_label;
            }
        }
    };

    const applyErrors = (payload) => {
        clearAllFieldErrors();

        const payloadErrors = payload && typeof payload.errors === "object" ? payload.errors : null;
        const explicitFields = Array.isArray(payload?.fields) ? payload.fields : [];

        if (payloadErrors) {
            Object.entries(payloadErrors).forEach(([fieldName, messages]) => {
                const firstMessage = Array.isArray(messages) && messages.length ? String(messages[0]) : "";
                setFieldError(fieldName, firstMessage);
            });
        } else {
            explicitFields.forEach((fieldName) => {
                setFieldError(fieldName);
            });
        }

        if (payload?.message) {
            const preferredField = explicitFields.includes("password")
                ? "password"
                : explicitFields[0];
            if (preferredField && !payloadErrors?.[preferredField]) {
                setFieldError(preferredField, payload.message);
            }
        }
    };

    const focusPrimaryErrorField = (payload) => {
        const fields = Array.isArray(payload?.fields) ? payload.fields : [];
        const preferredOrder = ["password", "username", "email", "identifier", "display_name", "confirm_password"];
        const targetName = preferredOrder.find((fieldName) => fields.includes(fieldName)) || fields[0] || null;
        const targetField = targetName ? form.elements.namedItem(targetName) : null;
        if (targetField instanceof HTMLElement) {
            targetField.focus();
            if (typeof targetField.select === "function" && targetName === "password") {
                targetField.select();
            }
        }
    };

    const setSubmittingState = (submitting) => {
        isSubmitting = submitting;
        form.setAttribute("aria-busy", submitting ? "true" : "false");

        if (submitButton) {
            submitButton.disabled = submitting;
            submitButton.textContent = submitting ? busyLabel : defaultButtonLabel;
        }
    };

    Array.from(form.elements).forEach((field) => {
        if (!(field instanceof HTMLElement) || !field.name) {
            return;
        }
        field.addEventListener("input", () => {
            clearFieldError(field.name);
            if (statusNode && !statusNode.hidden) {
                setStatus();
            }
            if (successMode === "inline") {
                hideResult();
            }
        });
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (isSubmitting) {
            return;
        }

        setStatus();
        clearAllFieldErrors();
        hideResult();
        setSubmittingState(true);

        try {
            const response = await fetch(form.action || window.location.href, {
                method: "POST",
                body: new FormData(form),
                credentials: "same-origin",
                headers: {
                    Accept: "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
            });
            const payload = await response.json().catch(() => null);

            if (response.ok && payload?.ok) {
                if (successMode === "redirect" && payload.redirect_url) {
                    navigate(payload.redirect_url);
                    return;
                }

                showResult(payload.result);
                return;
            }

            applyErrors(payload);
            setStatus({
                title: payload?.title || "Please check your details",
                message: payload?.message || "The request could not be completed.",
                tone: "error",
            });
            focusPrimaryErrorField(payload);
        } catch {
            setStatus({
                title: "Connection issue",
                message: "The request could not be completed. Please try again.",
                tone: "error",
            });
        } finally {
            setSubmittingState(false);
        }
    });
};

const initializeCustomSelect = (select) => {
    if (!select || select.multiple || select.dataset.customSelectReady === "true") {
        return null;
    }

    select.dataset.customSelectReady = "true";

    const shell = document.createElement("div");
    shell.className = "custom-select";
    if (select.classList.contains("is-invalid")) {
        shell.classList.add("is-invalid");
    }

    const button = document.createElement("button");
    button.className = "custom-select__button";
    button.type = "button";
    button.setAttribute("aria-haspopup", "listbox");
    button.setAttribute("aria-expanded", "false");

    const valueNode = document.createElement("span");
    valueNode.className = "custom-select__value";
    button.append(valueNode);

    const menu = document.createElement("div");
    menu.className = "custom-select__menu";
    menu.setAttribute("role", "listbox");

    const parent = select.parentNode;
    parent.insertBefore(shell, select);
    shell.append(select, button, menu);
    select.classList.add("native-select");
    select.tabIndex = -1;

    const options = [...select.options].map((option, index) => {
        const item = document.createElement("button");
        item.className = "custom-select__option";
        item.type = "button";
        item.setAttribute("role", "option");
        item.dataset.optionIndex = String(index);
        item.textContent = option.textContent;
        menu.append(item);
        return item;
    });

    const sync = () => {
        const selected = select.options[select.selectedIndex] || select.options[0];
        valueNode.textContent = selected ? selected.textContent : "";
        options.forEach((item, index) => {
            const isSelected = index === select.selectedIndex;
            item.classList.toggle("is-selected", isSelected);
            item.setAttribute("aria-selected", isSelected ? "true" : "false");
        });
    };

    const close = () => {
        shell.classList.remove("is-open");
        button.setAttribute("aria-expanded", "false");
    };

    const open = () => {
        document.querySelectorAll(".custom-select.is-open").forEach((item) => {
            if (item !== shell) {
                item.classList.remove("is-open");
                item.querySelector(".custom-select__button")?.setAttribute("aria-expanded", "false");
            }
        });
        shell.classList.add("is-open");
        button.setAttribute("aria-expanded", "true");
        options[select.selectedIndex]?.focus({ preventScroll: true });
    };

    const choose = (index) => {
        select.selectedIndex = index;
        select.dispatchEvent(new Event("change", { bubbles: true }));
        sync();
        close();
        button.focus({ preventScroll: true });
    };

    button.addEventListener("click", () => {
        if (shell.classList.contains("is-open")) {
            close();
        } else {
            open();
        }
    });

    button.addEventListener("keydown", (event) => {
        if (["Enter", " ", "ArrowDown", "ArrowUp"].includes(event.key)) {
            event.preventDefault();
            open();
        }
    });

    menu.addEventListener("click", (event) => {
        const option = event.target.closest(".custom-select__option");
        if (!option) {
            return;
        }
        choose(Number(option.dataset.optionIndex));
    });

    menu.addEventListener("keydown", (event) => {
        const activeIndex = options.indexOf(document.activeElement);
        if (event.key === "Escape") {
            event.preventDefault();
            close();
            button.focus({ preventScroll: true });
            return;
        }
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            if (activeIndex >= 0) {
                choose(activeIndex);
            }
            return;
        }
        if (event.key === "ArrowDown" || event.key === "ArrowUp") {
            event.preventDefault();
            const delta = event.key === "ArrowDown" ? 1 : -1;
            const nextIndex = (activeIndex + delta + options.length) % options.length;
            options[nextIndex]?.focus({ preventScroll: true });
            return;
        }
        if (event.key === "Home" || event.key === "End") {
            event.preventDefault();
            options[event.key === "Home" ? 0 : options.length - 1]?.focus({ preventScroll: true });
        }
    });

    select.addEventListener("change", sync);
    sync();
    return { shell, close };
};

document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const nav = document.querySelector(".nav-shell");
    const revealItems = [...document.querySelectorAll(".glass-panel, .product-card, .dashboard-card, .feature-tile, .quick-link")]
        .filter((item) => !item.closest("[data-flash-stack]"));
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let flashStack = document.querySelector("[data-flash-stack]");
    const authForms = document.querySelectorAll("[data-auth-form]");
    const customSelects = [...document.querySelectorAll("select.input")].map(initializeCustomSelect).filter(Boolean);

    const removeFlashStack = () => {
        if (!flashStack) {
            return;
        }

        const activeFlashStack = flashStack;
        flashStack = null;
        body.classList.remove("has-nav-feedback");
        activeFlashStack.classList.add("is-dismissing");

        const cleanup = () => activeFlashStack.remove();
        if (reducedMotion) {
            cleanup();
            return;
        }

        window.setTimeout(cleanup, 260);
    };

    const removeFlash = (flash) => {
        if (!flash) {
            return;
        }

        flash.classList.add("is-dismissing");

        const cleanup = () => {
            flash.remove();
            if (flashStack && !flashStack.querySelector("[data-flash]")) {
                removeFlashStack();
            }
        };

        if (reducedMotion) {
            cleanup();
            return;
        }

        window.setTimeout(cleanup, 240);
    };

    const syncNav = () => {
        if (!nav) {
            return;
        }
        nav.classList.toggle("is-scrolled", window.scrollY > 18);
    };

    const markPageReady = () => {
        if (reducedMotion) {
            body.classList.add("is-ready");
            return;
        }

        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                body.classList.add("is-ready");
                body.classList.remove("is-transitioning");
            });
        });
    };

    const isTransitionCandidate = (link) => {
        if (!link || reducedMotion) {
            return false;
        }

        const href = link.getAttribute("href");
        if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:")) {
            return false;
        }
        if (link.target && link.target !== "_self") {
            return false;
        }
        if (link.hasAttribute("download") || link.dataset.noTransition !== undefined) {
            return false;
        }

        const targetUrl = new URL(link.href, window.location.href);
        if (targetUrl.origin !== window.location.origin) {
            return false;
        }
        if (targetUrl.pathname === window.location.pathname && targetUrl.search === window.location.search) {
            return false;
        }

        return true;
    };

    const startPageTransition = (href) => {
        body.classList.add("is-transitioning");
        window.setTimeout(() => {
            window.location.href = href;
        }, 280);
    };

    document.addEventListener("click", (event) => {
        if (!event.target.closest(".custom-select")) {
            customSelects.forEach((select) => select.close());
        }

        const flashClose = event.target.closest("[data-flash-close]");
        if (flashClose) {
            removeFlash(flashClose.closest("[data-flash]"));
            return;
        }

        if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
            return;
        }

        const link = event.target.closest("a");
        if (!isTransitionCandidate(link)) {
            return;
        }

        event.preventDefault();
        startPageTransition(link.href);
    });

    window.addEventListener("pageshow", () => {
        body.classList.remove("is-transitioning");
        body.classList.add("is-ready");
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            customSelects.forEach((select) => select.close());
        }
        if (event.key === "Escape" && flashStack) {
            removeFlashStack();
        }
    });

    syncNav();
    window.addEventListener("scroll", syncNav, { passive: true });

    revealItems.forEach((item) => item.classList.add("reveal"));

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1 }
    );

    revealItems.forEach((item) => observer.observe(item));
    authForms.forEach((form) => {
        initializeAsyncAuthForm({
            form,
            reducedMotion,
            navigate: (href) => {
                if (!href) {
                    return;
                }
                if (reducedMotion) {
                    window.location.href = href;
                    return;
                }
                startPageTransition(href);
            },
        });
    });

    if (flashStack && flashStack.querySelector("[data-flash]")) {
        body.classList.add("has-nav-feedback");
    }

    markPageReady();
});
