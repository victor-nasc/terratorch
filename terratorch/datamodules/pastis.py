from typing import Any

import albumentations as A  # noqa: N812
from torch.utils.data import DataLoader, default_collate
from torchgeo.datamodules import NonGeoDataModule

from terratorch.datamodules.utils import wrap_in_compose_is_list, pad_collate
from terratorch.datasets import PASTIS


class PASTISDataModule(NonGeoDataModule):
    def __init__(
        self,
        batch_size: int = 8,
        num_workers: int = 0,
        data_root: str = "./",
        truncate_image: int | None = None,
        pad_image: int | None = None,
        train_transform: A.Compose | None | list[A.BasicTransform] = None,
        val_transform: A.Compose | None | list[A.BasicTransform] = None,
        test_transform: A.Compose | None | list[A.BasicTransform] = None,
        use_pad_collate: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            PASTIS,
            batch_size=batch_size,
            num_workers=num_workers,
            **kwargs,
        )
        self.truncate_image = truncate_image
        self.pad_image = pad_image
        self.collate_fn = pad_collate if use_pad_collate else default_collate
        self.train_transform = wrap_in_compose_is_list(train_transform)
        self.val_transform = wrap_in_compose_is_list(val_transform)
        self.test_transform = wrap_in_compose_is_list(test_transform)
        self.data_root = data_root
        self.kwargs = kwargs

    def setup(self, stage: str) -> None:
        if stage in ["fit"]:
            self.train_dataset = PASTIS(
                folds=[1, 2, 3],
                data_root=self.data_root,
                transform=self.train_transform,
                truncate_image=self.truncate_image,
                pad_image=self.pad_image,
                **self.kwargs,
            )
        if stage in ["fit", "validate"]:
            self.val_dataset = PASTIS(
                folds=[4],
                data_root=self.data_root,
                transform=self.val_transform,
                truncate_image=self.truncate_image,
                pad_image=self.pad_image,
                **self.kwargs,
            )
        if stage in ["test"]:
            self.test_dataset = PASTIS(
                folds=[5],
                data_root=self.data_root,
                transform=self.test_transform,
                truncate_image=self.truncate_image,
                pad_image=self.pad_image,
                **self.kwargs,
            )

    def _dataloader_factory(self, split: str) -> DataLoader:
        dataset = getattr(self, f"{split}_dataset")
        batch_size = self.batch_size
        return DataLoader(
            dataset=dataset,
            batch_size=batch_size,
            shuffle=split == "train",
            num_workers=self.num_workers,
            collate_fn=self.collate_fn,
            persistent_workers=self.num_workers > 0,
        )

    def train_dataloader(self) -> DataLoader:
        return self._dataloader_factory("train")

    def val_dataloader(self) -> DataLoader:
        return self._dataloader_factory("val")

    def test_dataloader(self) -> DataLoader:
        return self._dataloader_factory("test")
