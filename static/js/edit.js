document.addEventListener("DOMContentLoaded", () => {
    // Pastikan kolom "No" sudah diisi dari backend
    const noInput = document.getElementById("no");
    if (noInput && noInput.value) {
        console.log("Kolom 'No' sudah diisi dengan nomor:", noInput.value); // Debugging
    } else {
        console.error("Kolom 'No' tidak memiliki nilai. Pastikan data diteruskan dari backend.");
    }

    const form = document.getElementById("input-form");
    const cancelButton = document.getElementById("cancel-button");
    const createdInput = document.getElementById("created");
    const inTimeInput = document.getElementById("in_time");
    const outTimeInput = document.getElementById("out_time");
    const statusSelect = document.getElementById("status");
    const completedInput = document.getElementById("completed");
    const byInput = document.getElementById("by");

    // Fungsi untuk mendapatkan tanggal hari ini dalam format YYYY-MM-DD
    const getTodayDate = () => {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
    };

    // Fungsi untuk mendapatkan waktu sekarang dalam format HH:mm
    const getCurrentTime = () => {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, "0");
        const minutes = String(now.getMinutes()).padStart(2, "0");
        return `${hours}:${minutes}`;
    };

    // Perbarui nilai Completed dengan tanggal hari ini
    if (completedInput) {
        completedInput.value = getTodayDate();
        console.log("Kolom 'Completed' diperbarui dengan tanggal hari ini:", completedInput.value); // Debugging
    }

    // Perbarui nilai Out dengan waktu sekarang
    if (outTimeInput) {
        outTimeInput.value = getCurrentTime();
        console.log("Kolom 'Out' diperbarui dengan waktu sekarang:", outTimeInput.value); // Debugging
    }

    // Atur default pilihan "Status" ke "To Do" jika kosong
    if (statusSelect && !statusSelect.value) {
        statusSelect.value = "To Do";
        console.log("Kolom 'Status' diatur ke default 'To Do'"); // Debugging
    }

    // Fungsi untuk kembali ke halaman index
    const goToIndex = () => {
        window.location.href = "/";
    };

    // Fungsi untuk submit form
    const submitForm = () => {
        // Validasi kolom By
        if (!byInput.value || byInput.value.trim().toLowerCase() === "none") {
            alert("Kolom 'By' tidak boleh kosong atau bernilai 'None'.");
            byInput.focus(); // Fokuskan ke kolom By
            return; // Hentikan proses submit
        }

        // Isi kolom Completed dengan tanggal hari ini jika kosong
        if (completedInput && !completedInput.value) {
            completedInput.value = getTodayDate();
            console.log("Kolom 'Completed' diisi dengan tanggal hari ini:", completedInput.value); // Debugging
        }

        // Isi kolom Out dengan waktu sekarang jika kosong
        if (outTimeInput && !outTimeInput.value) {
            outTimeInput.value = getCurrentTime();
            console.log("Kolom 'Out' diisi dengan waktu sekarang:", outTimeInput.value); // Debugging
        }

        // Kirim data form menggunakan fetch
        const formData = new FormData(form);
        fetch(form.action, {
            method: "POST",
            body: formData,
        })
            .then((response) => {
                if (response.ok) {
                    // Tampilkan notifikasi sukses
                    Swal.fire({
                        icon: "success",
                        title: "Data Berhasil Disimpan",
                        text: "Anda akan diarahkan ke halaman utama.",
                        timer: 500, // Waktu tunggu sebelum redirect (0.5 detik)
                        showConfirmButton: false,
                    }).then(() => {
                        // Redirect ke halaman index
                        goToIndex();
                    });
                } else {
                    // Tampilkan notifikasi error
                    Swal.fire({
                        icon: "error",
                        title: "Gagal Menyimpan Data",
                        text: "Terjadi kesalahan saat menyimpan data. Silakan coba lagi.",
                    });
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                // Tampilkan notifikasi error
                Swal.fire({
                    icon: "error",
                    title: "Gagal Menyimpan Data",
                    text: "Terjadi kesalahan saat menyimpan data. Silakan coba lagi.",
                });
            });
    };

    // Tambahkan event listener untuk tombol submit
    form.addEventListener("submit", (event) => {
        event.preventDefault(); // Mencegah submit default
        submitForm(); // Panggil fungsi submitForm
    });

    // Tambahkan event listener untuk tombol Cancel
    if (cancelButton) {
        cancelButton.addEventListener("click", (event) => {
            event.preventDefault(); // Mencegah aksi default tombol
            goToIndex(); // Panggil fungsi goToIndex
        });
    }

    // Tambahkan event listener untuk tombol Enter dan Esc
    document.addEventListener("keydown", (event) => {
        console.log("Key pressed:", event.key); // Debugging
        if (event.key === "Enter") {
            event.preventDefault(); // Mencegah submit default jika fokus ada di input
            submitForm(); // Submit form
        } else if (event.key === "Escape") {
            event.preventDefault(); // Mencegah aksi default tombol
            console.log("Escape key pressed, redirecting to index..."); // Debugging
            goToIndex(); // Kembali ke halaman index
        }
    });
});
