// BootStrapのtooltipを動作させるために、JSで初期化する必要がある
if (document.querySelector('[data-bs-toggle="tooltip"]')) {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
}