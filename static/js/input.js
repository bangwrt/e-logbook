document.addEventListener("DOMContentLoaded", () => {
    const noInput = document.getElementById("no");

    if (!noInput) {
        console.error("Element with id 'no' not found.");
        return;
    }

    // Ambil nomor berikutnya dari backend
    fetch("/get_next_no", { method: "GET" })
        .then((response) => response.json())
        .then((data) => {
            if (data.next_no) {
                noInput.value = data.next_no;
            } else {
                console.warn("next_no is missing in the response");
            }
        })
        .catch((error) => {
            console.error("Error fetching next number:", error);
        });

    // Isi otomatis tanggal hari ini untuk kolom Created
    const createdInput = document.getElementById("created");
    if (createdInput) {
        const today = new Date().toISOString().split('T')[0];
        createdInput.value = today;
    }

    // Isi otomatis waktu sekarang untuk kolom In
    const inTimeInput = document.getElementById("in_time");
    if (inTimeInput) {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        inTimeInput.value = `${hours}:${minutes}`;
    }

    // Atur default pilihan Status ke "To Do"
    const statusSelect = document.getElementById("status");
    if (statusSelect) {
        statusSelect.value = "To Do";
    }

    // Fungsi untuk kembali ke halaman index
    const goToIndex = () => {
        window.location.href = "/";
    };

    // Fungsi untuk submit form
    const submitForm = () => {
        const form = document.getElementById("input-form");
        const formData = new FormData(form);
        console.log("Form data:", Object.fromEntries(formData.entries())); // Log data yang dikirimkan

        fetch(form.action, {
            method: "POST",
            body: formData,
        })
            .then((response) => {
                console.log("Response status:", response.status); // Log status respons
                if (!response.ok) {
                    throw new Error("HTTP error! status: " + response.status);
                }
                return response.json().catch((error) => {
                    console.error("Error parsing JSON:", error);
                    throw new Error("Respons dari server bukan JSON yang valid.");
                });
            })
            .then((data) => {
                console.log("Response data:", data); // Log data dari server
                if (data.success) {
                    Swal.fire({
                        icon: "success",
                        title: "Data Berhasil Ditambahkan",
                        text: "Anda akan diarahkan ke halaman utama.",
                        timer: 500,
                        showConfirmButton: false,
                    }).then(() => {
                        goToIndex();
                    });
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Gagal Menyimpan Data",
                        text: data.error || "Terjadi kesalahan saat menyimpan data. Silakan coba lagi.",
                    });
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                Swal.fire({
                    icon: "error",
                    title: "Gagal Menyimpan Data",
                    text: error.message || "Terjadi kesalahan saat menyimpan data. Silakan coba lagi.",
                });
            });
    };

    // Tambahkan event listener untuk tombol submit
    const form = document.getElementById("input-form");
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        submitForm();
    });


    // Tambahkan event listener untuk tombol Esc
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            event.preventDefault(); // Mencegah aksi default
            goToIndex(); // Panggil fungsi cancel
        }
    });
});
