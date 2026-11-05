import random
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from faker import Faker

from products.models import Category, Product
from purchases.models import Purchase
from sales.models import Sale


fake = Faker("fr_CA")


PRODUCT_CATALOG = [
    ("Coca-Cola 2L", "Boissons", Decimal("4.99")),
    ("Coca-Cola 1L", "Boissons", Decimal("2.99")),
    ("Coca-Cola Can 330 mL", "Boissons", Decimal("0.89")),
    ("Pepsi 2L", "Boissons", Decimal("4.49")),
    ("Pepsi Can 330 mL", "Boissons", Decimal("0.69")),
    ("Jus d'orange 1L", "Boissons", Decimal("5.29")),
    ("Eau de source 1.5L", "Boissons", Decimal("1.99")),
    ("Eau de source 1L", "Boissons", Decimal("1.39")),
    ("Eau de source 15L", "Boissons", Decimal("7.99")),

    ("Riz Basmati 5kg", "Alimentation", Decimal("18.99")),
    ("Pâtes Spaghetti 900g", "Alimentation", Decimal("3.99")),
    ("Farine tout usage 2.5kg", "Alimentation", Decimal("6.49")),
    ("Sucre blanc 2kg", "Alimentation", Decimal("5.79")),

    ("Lait 2% 2L", "Produits laitiers", Decimal("5.49")),
    ("Fromage Cheddar 400g", "Produits laitiers", Decimal("8.99")),
    ("Yogourt nature 750g", "Produits laitiers", Decimal("5.99")),
    ("Beurre salé 454g", "Produits laitiers", Decimal("7.49")),

    ("Chips nature 200g", "Snacks", Decimal("4.49")),
    ("Biscuits chocolat 300g", "Snacks", Decimal("4.99")),
    ("Barres granola x6", "Snacks", Decimal("5.29")),
    ("Arachides salées 500g", "Snacks", Decimal("6.49")),

    ("Savon Dove 4 unités", "Hygiène", Decimal("8.99")),
    ("Dentifrice Colgate 120ml", "Hygiène", Decimal("4.49")),
    ("Shampoing 400ml", "Hygiène", Decimal("7.99")),
    ("Papier hygiénique x12", "Hygiène", Decimal("12.99")),

    ("Liquide vaisselle 700ml", "Entretien", Decimal("4.99")),
    ("Nettoyant multi-surface 950ml", "Entretien", Decimal("5.99")),
    ("Détergent à lessive 2L", "Entretien", Decimal("14.99")),
    ("Sacs à déchets x40", "Entretien", Decimal("10.99")),

    ("Pain blanc tranché", "Boulangerie", Decimal("4.29")),
    ("Pain multigrain", "Boulangerie", Decimal("4.79")),
    ("Croissants x6", "Boulangerie", Decimal("6.99")),
    ("Bagels nature x6", "Boulangerie", Decimal("5.49")),

    ("Maïs en conserve 341ml", "Conserves", Decimal("2.49")),
    ("Tomates en dés 796ml", "Conserves", Decimal("3.29")),
    ("Haricots rouges 540ml", "Conserves", Decimal("2.99")),
    ("Thon en conserve 170g", "Conserves", Decimal("3.49")),
]


class Command(BaseCommand):

    help = "Génère des données de test réalistes et chronologiques."

    def add_arguments(self, parser):

        parser.add_argument(
            "--days",
            type=int,
            default=365,
        )

        parser.add_argument(
            "--purchases",
            type=int,
            default=200,
        )

        parser.add_argument(
            "--sales",
            type=int,
            default=500,
        )

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Supprime les données de test avant de quitter.",
        )

    def handle(self, *args, **options):

        if options["clear"]:
            self.clear_data()
            return

        number_days = options["days"]
        target_purchases = options["purchases"]
        target_sales = options["sales"]

        self.stdout.write(
            self.style.WARNING(
                "Génération des données..."
            )
        )

        with transaction.atomic():

            categories = self.create_categories()

            products = self.create_products(categories)

            self.generate_transactions(
                products=products,
                number_days=number_days,
                target_purchases=target_purchases,
                target_sales=target_sales,
            )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Données générées avec succès."
            )
        )

        self.stdout.write(
            f"""
Résumé
-------------------------
Catégories : {Category.objects.count()}
Produits    : {Product.objects.count()}
Achats      : {Purchase.objects.count()}
Ventes      : {Sale.objects.count()}
-------------------------
"""
        )

    def create_categories(self):

        category_names = sorted(
            {
                category
                for _, category, _ in PRODUCT_CATALOG
            }
        )

        categories = {}

        for name in category_names:

            category, _ = Category.objects.get_or_create(
                name=name
            )

            categories[name] = category

        return categories

    
    def create_products(self, categories):

        products = []

        for name, category_name, selling_price in PRODUCT_CATALOG:

            # Générer un prix d'achat estimé
            cost_ratio = Decimal(
                str(round(random.uniform(0.50, 0.80), 2))
            )

            purchase_price = (
                selling_price * cost_ratio
            ).quantize(Decimal("0.01"))

            # Recherche du produit existant
            product = Product.objects.filter(name=name).first()

            if product is None:

                # Générer un SKU unique
                last_product = Product.objects.order_by("-id").first()

                next_id = last_product.id + 1 if last_product else 1

                sku = f"PRD-{next_id:05d}"

                # Éviter les collisions avec les SKU existants
                while Product.objects.filter(sku=sku).exists():
                    next_id += 1
                    sku = f"PRD-{next_id:05d}"

                product = Product.objects.create(
                    sku=sku,
                    name=name,
                    category=categories[category_name],
                    purchase_price=purchase_price,
                    selling_price=selling_price,
                    stock=0,
                    is_active=True,
                )

            else:

                # Mettre à jour les informations existantes
                product.category = categories[category_name]
                product.selling_price = selling_price
                product.is_active = True

                # Conserver le prix d'achat existant
                product.save(
                    update_fields=[
                        "category",
                        "selling_price",
                        "is_active",
                    ]
                )

            products.append(product)

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(products)} produits disponibles."
            )
        )

        return products


    def generate_transactions(
    self,
    products,
    number_days,
    target_purchases,
    target_sales,
    ):

        # 1. Vérifier les paramètres

        if number_days < 0:
            raise CommandError(
                "--days doit être positif ou nul."
            )

        if target_purchases < 0 or target_sales < 0:
            raise CommandError(
                "Le nombre de transactions ne peut pas être négatif."
            )

        if target_sales > 0 and target_purchases == 0:
            raise CommandError(
                "Prévoyez au moins un achat pour générer des ventes."
            )

        if not products and (target_purchases or target_sales):
            raise CommandError("Aucun produit disponible.")

        # 2. Définir la période

        end_date = timezone.localdate()
        start_date = end_date - timedelta(days=number_days)

        # 3. Construire le calendrier des transactions

        events = []

        for i in range(target_purchases):

            # Un achat initial garantit du stock au début.
            day_offset = (
                0 if i == 0
                else random.randint(0, number_days)
            )

            date = start_date + timedelta(days=day_offset)

            events.append((date, 0, "purchase"))

        for _ in range(target_sales):

            day_offset = random.randint(0, number_days)

            date = start_date + timedelta(days=day_offset)

            events.append((date, 1, "sale"))

        # Sur une même date, les achats passent avant les ventes.
        events.sort(key=lambda event: (event[0], event[1]))

        # 4. Définir les quantités d'approvisionnement

        # Chaque vente vend au maximum 8 unités.
        # La quantité minimale achetée garantit une réserve
        # globale suffisante pour les ventes demandées.

        if target_purchases:
            min_purchase_quantity = max(
                40,
                (target_sales * 8 + target_purchases - 1)
                // target_purchases,
            )
        else:
            min_purchase_quantity = 40

        max_purchase_quantity = max(
            80,
            min_purchase_quantity + 20,
        )

        purchases_created = 0
        sales_created = 0

        # Synchroniser les stocks initialement chargés.
        for product in products:
            product.refresh_from_db(fields=["stock"])

        def create_purchase(product, date):

            cost_ratio = Decimal(
                str(round(random.uniform(0.50, 0.80), 2))
            )

            purchase_price = (
                product.selling_price * cost_ratio
            ).quantize(Decimal("0.01"))

            quantity = random.randint(
                min_purchase_quantity,
                max_purchase_quantity,
            )

            Purchase.objects.create(
                supplier=fake.company(),
                product=product,
                quantity=quantity,
                unit_price=purchase_price,
                date=date,
            )

            # Le signal a modifié la base de données.
            # Actualiser l'objet Python.
            product.refresh_from_db(fields=["stock"])

        # 5. Exécuter les transactions chronologiquement

        # Indices des achats anticipés pour éviter de
        # les enregistrer une seconde fois.
        consumed_events = set()

        with transaction.atomic():

            for index, (current_date, _, event_type) in enumerate(events):

                if index in consumed_events:
                    continue

                if event_type == "purchase":

                    product = random.choice(products)

                    create_purchase(product, current_date)

                    purchases_created += 1

                else:

                    products_in_stock = [
                        product
                        for product in products
                        if product.stock > 0
                    ]

                    # En cas de rupture générale, avancer
                    # un approvisionnement futur.
                    if not products_in_stock:

                        future_purchase_index = next(
                            (
                                j
                                for j in range(index + 1, len(events))
                                if j not in consumed_events
                                and events[j][2] == "purchase"
                            ),
                            None,
                        )

                        if future_purchase_index is None:
                            raise CommandError(
                                "Stock insuffisant et aucun "
                                "réapprovisionnement disponible."
                            )

                        product = random.choice(products)

                        create_purchase(product, current_date)

                        purchases_created += 1
                        consumed_events.add(future_purchase_index)

                        products_in_stock = [
                            product
                        ]

                    product = random.choice(products_in_stock)

                    quantity = random.randint(
                        1,
                        min(8, product.stock),
                    )

                    Sale.objects.create(
                        product=product,
                        quantity=quantity,
                        unit_price=product.selling_price,
                        date=current_date,
                    )

                    # Actualiser le stock après le signal.
                    product.refresh_from_db(fields=["stock"])

                    sales_created += 1

        # 6. Afficher le résultat

        self.stdout.write(
            self.style.SUCCESS(
                f"{purchases_created} achats créés."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{sales_created} ventes créées."
            )
        )