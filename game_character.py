import random
class Character:
    """
    Base class untuk semua karakter dalam game.
    Menggunakan encapsulation dengan private/protected attributes.
    """

    # Class variable - level maksimum yang bisa dicapai
    MAX_LEVEL = 10

    def __init__(self, nama: str, hp: int, attack: int, defense: int):
        """
        Constructor utama karakter.

        Args:
            nama    : Nama karakter
            hp      : Health Points (nyawa)
            attack  : Nilai serangan
            defense : Nilai pertahanan
        """
        # Protected attributes (dapat diakses oleh subclass)
        self._nama    = nama
        self._hp_max  = hp          # HP maksimum
        self._hp      = hp          # HP saat ini
        self._attack  = attack
        self._defense = defense
        self._level   = 1           # Level awal selalu 1
        self._exp     = 0           # Experience points
        self._exp_to_levelup = 100  # EXP yang dibutuhkan untuk naik level

    # ── Getter Properties ─────────────────────────────────────
    @property
    def nama(self) -> str:
        return self._nama

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def hp_max(self) -> int:
        return self._hp_max

    @property
    def attack(self) -> int:
        return self._attack

    @property
    def defense(self) -> int:
        return self._defense

    @property
    def level(self) -> int:
        return self._level

    @property
    def is_alive(self) -> bool:
        """Return True jika karakter masih hidup."""
        return self._hp > 0

    # ── Methods ───────────────────────────────────────────────
    def tampilkan_status(self) -> None:
        """Menampilkan status lengkap karakter."""
        hp_bar = self._buat_hp_bar()
        print(f"""
┌─────────────────────────────────────┐
│  {self._nama:<35} │
│  Kelas  : {self.__class__.__name__:<26} │
│  Level  : {self._level:<26} │
│  HP     : {self._hp}/{self._hp_max:<22} │
│  HP Bar : {hp_bar:<26} │
│  ATK    : {self._attack:<26} │
│  DEF    : {self._defense:<26} │
│  EXP    : {self._exp}/{self._exp_to_levelup:<19} │
└─────────────────────────────────────┘""")

    def serang(self, target: 'Character') -> int:
        """
        Menyerang karakter lain.

        Args:
            target : Karakter yang diserang

        Returns:
            int: Damage yang diberikan
        """
        if not self.is_alive:
            print(f"  ✗ {self._nama} sudah kalah dan tidak bisa menyerang!")
            return 0

        if not target.is_alive:
            print(f"  ✗ {target.nama} sudah kalah!")
            return 0

        # Hitung damage: attack - setengah defense target (minimal 1)
        raw_damage  = self._attack + random.randint(-5, 5)   # sedikit random
        damage_reduction = target.defense // 2
        final_damage = max(1, raw_damage - damage_reduction)

        # Chance critical hit 15%
        is_critical = random.random() < 0.15
        if is_critical:
            final_damage = int(final_damage * 1.5)

        target._terima_damage(final_damage)

        crit_text = " [CRITICAL!]" if is_critical else ""
        print(f"  ⚔  {self._nama} menyerang {target.nama}"
              f" → -{final_damage} HP{crit_text}")

        if not target.is_alive:
            print(f"  ✝  {target.nama} telah dikalahkan!")
            self._gain_exp(50)

        return final_damage

    def level_up(self) -> None:
        """Menaikkan level karakter dan meningkatkan stats."""
        if self._level >= Character.MAX_LEVEL:
            print(f"  ★  {self._nama} sudah mencapai level maksimum ({Character.MAX_LEVEL})!")
            return

        self._level   += 1
        self._exp     -= self._exp_to_levelup
        self._exp_to_levelup = int(self._exp_to_levelup * 1.3)  # EXP makin banyak dibutuhkan

        # Tingkatkan stats dasar saat level up
        hp_bonus      = 20
        attack_bonus  = 3
        defense_bonus = 2

        self._hp_max  += hp_bonus
        self._hp       = min(self._hp + hp_bonus, self._hp_max)  # heal sebagian
        self._attack  += attack_bonus
        self._defense += defense_bonus

        print(f"""
  ★  {self._nama} NAIK LEVEL! → Level {self._level}
     HP    +{hp_bonus} → {self._hp_max}
     ATK   +{attack_bonus} → {self._attack}
     DEF   +{defense_bonus} → {self._defense}""")

    # ── Protected/Private Helpers ─────────────────────────────
    def _terima_damage(self, damage: int) -> None:
        """Mengurangi HP karakter (protected)."""
        self._hp = max(0, self._hp - damage)

    def _gain_exp(self, exp: int) -> None:
        """Menambahkan EXP dan auto level-up jika cukup."""
        self._exp += exp
        print(f"  ✦  {self._nama} mendapatkan +{exp} EXP")
        if self._exp >= self._exp_to_levelup and self._level < Character.MAX_LEVEL:
            self.level_up()

    def _heal(self, amount: int) -> None:
        """Method heal yang bisa digunakan subclass."""
        healed = min(amount, self._hp_max - self._hp)
        self._hp += healed
        print(f"  ♥  {self._nama} memulihkan {healed} HP → {self._hp}/{self._hp_max}")

    def _buat_hp_bar(self, panjang: int = 15) -> str:
        """Membuat visual HP bar."""
        rasio  = self._hp / self._hp_max
        terisi = int(rasio * panjang)
        kosong = panjang - terisi
        return f"[{'█' * terisi}{'░' * kosong}]"

    def __str__(self) -> str:
        return f"{self._nama} (Lv.{self._level} {self.__class__.__name__})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(nama='{self._nama}', level={self._level})"


# ============================================================
# CLASS TURUNAN 1: Warrior
# ============================================================
class Warrior(Character):
    """
    Warrior: Tank dengan HP & Defense tinggi.
    Skill khusus: Shield Bash & Berserker Mode
    """

    def __init__(self, nama: str):
        # Warrior: HP & defense tinggi, attack sedang
        super().__init__(
            nama    = nama,
            hp      = 180,
            attack  = 35,
            defense = 25
        )
        # Atribut khusus Warrior
        self.__shield_bash_cooldown = 0   # private - cooldown skill
        self.__berserker_active     = False

    def tampilkan_status(self) -> None:
        """Override untuk menampilkan info tambahan Warrior."""
        super().tampilkan_status()
        mode = "AKTIF ⚡" if self.__berserker_active else "Tidak aktif"
        print(f"  [Warrior] Berserker: {mode} | "
              f"Shield Bash CD: {self.__shield_bash_cooldown}")

    def shield_bash(self, target: 'Character') -> None:
        """
        Skill Warrior: Memukul musuh dengan perisai.
        Damage tinggi + efek stun (mengurangi DEF target sementara).
        Cooldown: 2 turn setelah digunakan.
        """
        if self.__shield_bash_cooldown > 0:
            print(f"  ✗ Shield Bash masih cooldown ({self.__shield_bash_cooldown} turn lagi)!")
            return

        if not target.is_alive:
            print(f"  ✗ {target.nama} sudah kalah!")
            return

        bash_damage = int(self._attack * 1.8)
        target._terima_damage(bash_damage)
        # Sementara kurangi defense target
        target._defense = max(0, target._defense - 10)

        self.__shield_bash_cooldown = 2
        print(f"  🛡  {self._nama} menggunakan SHIELD BASH!"
              f" → {target.nama} -{bash_damage} HP, DEF -10!")

        if not target.is_alive:
            print(f"  ✝  {target.nama} telah dikalahkan!")
            self._gain_exp(50)

    def berserker_mode(self) -> None:
        """
        Skill Warrior: Mode berserk — tingkatkan ATK 50% tapi DEF -30%.
        Berlangsung hingga akhir pertarungan.
        """
        if self.__berserker_active:
            print(f"  ✗ {self._nama} sudah dalam Berserker Mode!")
            return

        self.__berserker_active = True
        self._attack  = int(self._attack * 1.5)
        self._defense = int(self._defense * 0.7)
        print(f"  ⚡ {self._nama} masuk BERSERKER MODE! ATK meningkat, DEF berkurang!")

    def reduce_cooldown(self) -> None:
        """Kurangi cooldown setiap turn."""
        if self.__shield_bash_cooldown > 0:
            self.__shield_bash_cooldown -= 1


# ============================================================
# CLASS TURUNAN 2: Mage
# ============================================================
class Mage(Character):
    """
    Mage: Damage & utility tinggi, tapi HP & Defense rendah.
    Skill khusus: Fireball, Arcane Shield, Heal
    """

    def __init__(self, nama: str):
        # Mage: ATK sangat tinggi, HP & DEF rendah
        super().__init__(
            nama    = nama,
            hp      = 100,
            attack  = 55,
            defense = 10
        )
        # Atribut khusus Mage
        self._mana     = 150     # Protected - resource untuk skill
        self._mana_max = 150

    def tampilkan_status(self) -> None:
        """Override untuk menampilkan Mana Mage."""
        super().tampilkan_status()
        mana_bar = self._buat_mana_bar()
        print(f"  [Mage] Mana: {self._mana}/{self._mana_max} {mana_bar}")

    def fireball(self, target: 'Character') -> None:
        """
        Skill Mage: Luncurkan bola api dengan damage AOE tinggi.
        Biaya: 40 Mana
        """
        mana_cost = 40
        if self._mana < mana_cost:
            print(f"  ✗ Mana tidak cukup! (Butuh {mana_cost}, punya {self._mana})")
            return

        if not target.is_alive:
            print(f"  ✗ {target.nama} sudah kalah!")
            return

        self._mana -= mana_cost
        fire_damage = int(self._attack * 2.0) + random.randint(10, 30)
        target._terima_damage(fire_damage)

        print(f"  🔥 {self._nama} meluncurkan FIREBALL!"
              f" → {target.nama} -{fire_damage} HP! (Mana: {self._mana})")

        if not target.is_alive:
            print(f"  ✝  {target.nama} telah dikalahkan!")
            self._gain_exp(50)

    def arcane_shield(self) -> None:
        """
        Skill Mage: Buat perisai sihir — tingkatkan DEF sementara +25.
        Biaya: 25 Mana
        """
        mana_cost = 25
        if self._mana < mana_cost:
            print(f"  ✗ Mana tidak cukup! (Butuh {mana_cost}, punya {self._mana})")
            return

        self._mana    -= mana_cost
        self._defense += 25
        print(f"  🔮 {self._nama} mengaktifkan ARCANE SHIELD! DEF +25 → {self._defense}"
              f" (Mana: {self._mana})")

    def heal(self, target: 'Character' = None) -> None:
        """
        Skill Mage: Menyembuhkan diri sendiri atau karakter lain.
        Biaya: 30 Mana
        """
        mana_cost = 30
        if self._mana < mana_cost:
            print(f"  ✗ Mana tidak cukup! (Butuh {mana_cost}, punya {self._mana})")
            return

        self._mana -= mana_cost
        heal_amount = 50 + random.randint(0, 20)

        if target is None or target == self:
            self._heal(heal_amount)
            print(f"  💊 {self._nama} menggunakan HEAL pada diri sendiri! (Mana: {self._mana})")
        else:
            target._heal(heal_amount)
            print(f"  💊 {self._nama} menggunakan HEAL pada {target.nama}! (Mana: {self._mana})")

    def meditate(self) -> None:
        """Memulihkan sebagian Mana."""
        regen = 50
        self._mana = min(self._mana_max, self._mana + regen)
        print(f"  🧘 {self._nama} bermeditasi, Mana +{regen} → {self._mana}/{self._mana_max}")

    def _buat_mana_bar(self, panjang: int = 10) -> str:
        """Visual bar untuk Mana."""
        rasio  = self._mana / self._mana_max
        terisi = int(rasio * panjang)
        return f"[{'▓' * terisi}{'░' * (panjang - terisi)}]"


# ============================================================
# CLASS TURUNAN 3: Archer
# ============================================================
class Archer(Character):
    """
    Archer: Kecepatan tinggi, damage kritis, serangan jarak jauh.
    Skill khusus: Rapid Shot, Snipe, Evasion
    """

    def __init__(self, nama: str):
        # Archer: ATK sedang, critical chance tinggi, speed tinggi
        super().__init__(
            nama    = nama,
            hp      = 130,
            attack  = 42,
            defense = 15
        )
        # Atribut khusus Archer
        self.__arrows         = 20      # Jumlah anak panah
        self.__evasion_active = False   # Status menghindar
        self.__crit_chance    = 0.30    # 30% chance critical

    def tampilkan_status(self) -> None:
        """Override untuk menampilkan info Archer."""
        super().tampilkan_status()
        evade = "Aktif ⚡" if self.__evasion_active else "Tidak aktif"
        print(f"  [Archer] Panah: {self.__arrows} | "
              f"Crit Chance: {int(self.__crit_chance * 100)}% | "
              f"Evasion: {evade}")

    def serang(self, target: 'Character') -> int:
        """
        Override serangan dasar Archer — critical chance lebih tinggi.
        """
        if not self.is_alive or not target.is_alive:
            return super().serang(target)

        if self.__arrows <= 0:
            print(f"  ✗ {self._nama} kehabisan anak panah! Menggunakan serangan fisik.")
            return super().serang(target)

        self.__arrows -= 1
        raw_damage   = self._attack + random.randint(0, 10)
        final_damage = max(1, raw_damage - target.defense // 3)

        is_critical = random.random() < self.__crit_chance
        if is_critical:
            final_damage = int(final_damage * 2.0)

        target._terima_damage(final_damage)

        crit_text = " [CRITICAL! ×2]" if is_critical else ""
        print(f"  🏹 {self._nama} melepaskan panah ke {target.nama}"
              f" → -{final_damage} HP{crit_text} (Panah: {self.__arrows})")

        if not target.is_alive:
            print(f"  ✝  {target.nama} telah dikalahkan!")
            self._gain_exp(50)

        return final_damage

    def rapid_shot(self, target: 'Character') -> None:
        """
        Skill Archer: Tembakkan 3 panah sekaligus dengan cepat.
        Menghabiskan 3 anak panah.
        """
        shots_needed = 3
        if self.__arrows < shots_needed:
            print(f"  ✗ Panah tidak cukup! (Butuh {shots_needed}, punya {self.__arrows})")
            return

        if not target.is_alive:
            print(f"  ✗ {target.nama} sudah kalah!")
            return

        print(f"  🏹🏹🏹 {self._nama} menggunakan RAPID SHOT!")
        total_damage = 0
        for i in range(shots_needed):
            dmg = max(1, int(self._attack * 0.7) + random.randint(-5, 5))
            target._terima_damage(dmg)
            total_damage += dmg
            self.__arrows -= 1
            print(f"      Panah {i+1}: -{dmg} HP")

        print(f"  Total damage: {total_damage} | Panah tersisa: {self.__arrows}")

        if not target.is_alive:
            print(f"  ✝  {target.nama} telah dikalahkan!")
            self._gain_exp(50)

    def snipe(self, target: 'Character') -> None:
        """
        Skill Archer: Bidikan mematikan yang mengabaikan defense.
        Menghabiskan 2 anak panah.
        """
        if self.__arrows < 2:
            print(f"  ✗ Panah tidak cukup untuk Snipe! (Butuh 2, punya {self.__arrows})")
            return

        if not target.is_alive:
            print(f"  ✗ {target.nama} sudah kalah!")
            return

        self.__arrows -= 2
        # Snipe mengabaikan defense sepenuhnya
        snipe_damage = int(self._attack * 1.6) + random.randint(15, 35)

        target._terima_damage(snipe_damage)
        print(f"  🎯 {self._nama} menggunakan SNIPE!"
              f" → {target.nama} -{snipe_damage} HP (Ignore DEF!) "
              f"(Panah: {self.__arrows})")

        if not target.is_alive:
            print(f"  ✝  {target.nama} telah dikalahkan!")
            self._gain_exp(50)

    def evasion(self) -> None:
        """
        Skill Archer: Aktifkan mode menghindar — DEF +20, tambah crit chance.
        """
        if self.__evasion_active:
            print(f"  ✗ {self._nama} sudah dalam Evasion Mode!")
            return

        self.__evasion_active  = True
        self._defense         += 20
        self.__crit_chance    += 0.15   # +15% crit chance
        print(f"  💨 {self._nama} mengaktifkan EVASION!"
              f" DEF +20, Crit +15% → {int(self.__crit_chance * 100)}%")

    def collect_arrows(self) -> None:
        """Kumpulkan anak panah kembali."""
        collected = random.randint(5, 10)
        self.__arrows += collected
        print(f"  🏹 {self._nama} mengumpulkan {collected} anak panah. "
              f"Total: {self.__arrows}")


# ============================================================
# FUNGSI HELPER UNTUK MAIN PROGRAM
# ============================================================
def cetak_pembatas(judul: str = "") -> None:
    """Mencetak garis pembatas dengan judul opsional."""
    if judul:
        padding = (50 - len(judul)) // 2
        print(f"\n{'═' * padding} {judul} {'═' * padding}")
    else:
        print("\n" + "═" * 52)


def tampilkan_semua_status(karakter_list: list) -> None:
    """Menampilkan status semua karakter dalam daftar."""
    for karakter in karakter_list:
        karakter.tampilkan_status()


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":

    cetak_pembatas("SISTEM KARAKTER GAME - RPG SIMULATOR")
    print("  Selamat datang di simulasi pertarungan RPG!")

    # ─── 1. INSTANSIASI KARAKTER ─────────────────────────────
    cetak_pembatas("MEMBUAT KARAKTER")

    warrior = Warrior("Aldric si Baja")
    mage    = Mage("Seraphina")
    archer  = Archer("Ryn si Bayangan")

    print("  Tiga karakter telah dibuat:")
    print(f"  • {warrior}")
    print(f"  • {mage}")
    print(f"  • {archer}")

    # ─── 2. TAMPILKAN STATUS AWAL ─────────────────────────────
    cetak_pembatas("STATUS AWAL KARAKTER")
    tampilkan_semua_status([warrior, mage, archer])

    # ─── 3. SIMULASI PERTARUNGAN ──────────────────────────────
    cetak_pembatas("BABAK 1 — SERANGAN AWAL")

    print("\n  >> Warrior menyerang Archer...")
    warrior.serang(archer)

    print("\n  >> Archer membalas dengan Rapid Shot ke Warrior...")
    archer.rapid_shot(warrior)

    print("\n  >> Mage menggunakan Fireball ke Warrior!")
    mage.fireball(warrior)

    cetak_pembatas("BABAK 2 — SKILL KHUSUS")

    print("\n  >> Warrior mengaktifkan Berserker Mode!")
    warrior.berserker_mode()

    print("\n  >> Warrior menggunakan Shield Bash ke Archer!")
    warrior.shield_bash(archer)

    print("\n  >> Mage mengaktifkan Arcane Shield...")
    mage.arcane_shield()

    print("\n  >> Archer mengaktifkan Evasion!")
    archer.evasion()

    cetak_pembatas("BABAK 3 — SERANGAN LANJUTAN")

    print("\n  >> Archer menggunakan Snipe ke Mage!")
    archer.snipe(mage)

    print("\n  >> Mage menyembuhkan dirinya sendiri!")
    mage.heal()

    print("\n  >> Mage menyembuhkan Archer yang terluka!")
    mage.heal(archer)

    print("\n  >> Warrior menyerang Mage!")
    warrior.serang(mage)

    print("\n  >> Archer mengumpulkan anak panah...")
    archer.collect_arrows()

    print("\n  >> Archer menyerang Warrior dengan Rapid Shot!")
    archer.rapid_shot(warrior)

    cetak_pembatas("LEVEL UP!")

    print("\n  >> Semua karakter mendapatkan EXP dari pertarungan...")
    # Simulasi gain EXP
    warrior._gain_exp(80)
    mage._gain_exp(95)
    archer._gain_exp(85)

    print("\n  >> Archer berhasil Level Up manual!")
    archer.level_up()

    cetak_pembatas("MEDITASI & RECOVERY")

    print("\n  >> Mage bermeditasi untuk memulihkan Mana...")
    mage.meditate()

    print("\n  >> Warrior menggunakan Shield Bash setelah cooldown...")
    warrior.reduce_cooldown()
    warrior.reduce_cooldown()
    warrior.shield_bash(archer)

    # ─── 4. STATUS AKHIR ──────────────────────────────────────
    cetak_pembatas("STATUS AKHIR SETELAH PERTARUNGAN")
    tampilkan_semua_status([warrior, mage, archer])

    # ─── 5. RINGKASAN ─────────────────────────────────────────
    cetak_pembatas("RINGKASAN PERTARUNGAN")

    karakter_list = [warrior, mage, archer]
    print()
    for k in karakter_list:
        status = "✓ Hidup" if k.is_alive else "✝ Kalah"
        hp_pct = int((k.hp / k.hp_max) * 100)
        print(f"  {status}  {k.nama:<22} "
              f"Lv.{k.level}  HP: {k.hp}/{k.hp_max} ({hp_pct}%)")

    hidup  = sum(1 for k in karakter_list if k.is_alive)
    kalah  = len(karakter_list) - hidup
    print(f"\n  Total hidup: {hidup} | Total kalah: {kalah}")

    cetak_pembatas("SIMULASI SELESAI")
    print("  Terima kasih telah bermain! ⚔\n")
