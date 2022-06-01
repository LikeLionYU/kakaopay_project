from django.db import models

class Shopping(models.Model):
    item_name = models.CharField(max_length=100)
    item_price = models.IntegerField()
    quantity = models.IntegerField()
    total_amount = models.IntegerField()
    tax_free_amount = models.FloatField()
    shopped_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name

